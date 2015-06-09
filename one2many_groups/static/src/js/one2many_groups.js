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
                            if(group.parent_id){
                                parent_row = self.$current.find('tr[data-group_id="'+group.parent_id[0]+'"]');
                                parent_group_level = parent_row.attr('group_level');
                                group_row.addClass('oe_group_level'+group.level);
                                group_row.insertAfter(self.$current.find('.oe_group_level'+parent_group_level+':last'));
                            }
                            else{
                                group_row.addClass('oe_group_level'+group.level);
                                self.$current.prepend(group_row);
                            }
                            curr_last = group_row;
                            $.each(group.members_ids, function(key, id){
                                curr = self.$current.find('tr[data-id='+id+']');
                                curr.addClass(group_row.attr('class'));
                                curr.insertAfter(curr_last);
                                curr_last = curr;
                            });
                        });
                    }
                }
            });
}