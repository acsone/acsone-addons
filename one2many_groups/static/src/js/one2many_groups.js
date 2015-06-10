openerp.one2many_groups = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt, QWeb = instance.web.qweb;
    GridTriggerKey = 'TreeGrid';

    instance.web.form.widgets.add('x2many_tree_grid',
            'instance.one2many_groups.TreeGrid');
    instance.one2many_groups.TreeGrid = instance.web.ListView.List
            .include({
                group_fields : [ 'name', 'sequence', 'parent_id',
                        'members_ids', 'children_ids', 'master_id', 'level' ],
                init : function(parent, dataset, view_id, options) {
                    res = this._super(parent, dataset, view_id, options);
                    return res;
                },
                start : function() {
                    res = this._super.apply(this, arguments);
                    return res;
                },
                render : function() {
                    var self = this;
                    res = self._super.apply(this, arguments);
                    context = openerp.web.pyeval.eval('contexts',
                            self.dataset.context);
                    if (GridTriggerKey in context && context[GridTriggerKey]) {
                        self.dataset
                            .call('get_cls_group')
                            .done(function(result){
                                domain = [['master_id', '=', self.dataset.parent_view.datarecord.id]];
                                new instance.web.Model(result, self.dataset.context)
                                    .call('search_read', [domain,self.group_fields])
                                    .done(function(result){
                                        self.setup_groups_view(result);
                                    });
                            });
                    }
                    return res;
                },
                setup_groups_view: function(groups){
                    var self = this;
                    if(!groups.length){
                        self.$current.prepend(
                            QWeb.render('TreeGrid.add_group'));
                    }
                    else{
                        $.each(groups, function(key, group){
                            group_row = $(QWeb.render('TreeGrid.group_row',{
                                group:group,
                            }));
                            row_class = 'oe_group_level'+group.level;
                            if(group.parent_id){
                                parent_row = self.$current.find('tr[data-group_id="'+group.parent_id[0]+'"]');
                                parent_group_level = parent_row.attr('group_level');
                                row_class = parent_row.attr('class') + ' ' + row_class;
                                group_row.addClass(row_class);
                                group_row.insertAfter(self.$current.find('.oe_group_level'+parent_group_level+':last'));
                            }
                            else{
                                group_row.addClass(row_class);
                                self.$current.prepend(group_row);
                            }
                            vision_controller = self.$current.find('i#vision_controller'+group.id);
                            vision_controller.addClass(row_class);
                            self.init_controller_vision(group_row, vision_controller);
                            curr_last = group_row;
                            $.each(group.members_ids, function(key, id){
                                curr = self.$current.find('tr[data-id='+id+']');
                                curr.attr('row_level', group.level);
                                curr.addClass(group_row.attr('class'));
                                curr.insertAfter(curr_last);
                                curr_last = curr;
                            });
                        });
                    }
                },
                init_controller_vision: function(row, el){
                    var self = this;
                    el.bind('click', function(event){
                        vision_controller = $(event.target);
                        row_class = 'oe_group_level' + row.attr('group_level');

                        if(vision_controller.hasClass('fa-arrow-right')){
                            // show only the same level elements
                            vision_controller
                                                .removeClass('fa-arrow-right')
                                                .addClass('fa-arrow-down');
                            row_level = row.attr('group_level');
                            group_level = parseInt(row_level) + 1;
                            elements = self.$current
                                                    .find('tr[row_level="'+row_level+'"], tr[group_level="'+group_level+'"]');
                            elements.removeClass('hidden');
                        }
                        else{
                            // hide all sub-level
                            self.$current.find('i.'+row_class)
                                                                .removeClass('fa-arrow-down')
                                                                .addClass('fa-arrow-right');
                            elements = self.$current
                                                        .find('tr.'+row_class)
                                                        .not(self.$current.find('tr[data-group_id="'+row.attr('data-group_id')+'"]'));
                            elements.addClass('hidden');
                        }
                    });
                }
            });
}