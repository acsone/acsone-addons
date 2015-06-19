openerp.one2many_groups = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt, QWeb = instance.web.qweb;
    GridTriggerKey = 'TreeGrid';

    instance.web.form.FormWidget
            .include({
                build_context: function() {
                    if(this.dataset && this.dataset.TreeGridMode){
                        context = openerp.web.pyeval.eval('contexts',
                                this.dataset.context);
                        this.node.attrs.context = JSON.stringify(context);
                    }
                    return this._super.apply(this, arguments);
                }
            });
    instance.web.ListView.Groups
            .include({
                get_seqname: function(){
                    var sequence_field = _(this.columns).find(function (c) {
                        return c.widget === 'handle';
                    });
                    return sequence_field ? sequence_field.name : 'sequence';
                },
                resequence_rows_stop: function(list, dataset, event, ui){
                    var self = this;
                        seqname = self.get_seqname();
                        field_group = 'abstract_group_id',
                        curr = ui.item,
                        curr_id = curr.data('id'),
                        curr_record = list.records.get(curr_id),
                        prev = ui.item.prev(),
                        prev_id = prev.data('id'),
                        prev_group_id = prev.data('group_id') ? prev.
                                data('group_id') : list.records.get(prev_id).get(field_group)[0],
                        seq = prev.data('id') ? list.records.get(prev_id).get(seqname) + 1 : 0,
                        fct = function (dataset, id, vals) {
                            $.async_when().done(function () {
                                dataset.write(id, vals);
                            });
                        };
                    var to_update,
                        vals = {};
                    vals[seqname] = seq;
                    if(curr_record.get(field_group)[0]!=prev_group_id){
                        to_update = curr.nextAll();
                        vals[field_group] = prev_group_id;
                        fct(dataset, curr_id, vals);
                        curr_record.set(seqname, seq);
                        curr_record.set(field_group, prev_group_id);
                        list.set_node_member_attr(curr, $(list.$current.find('tr[data-id="'+curr_id+'"]')));
                        seq++;
                    }
                    else{
                        to_update = curr.nextAll().andSelf();
                    }
                    $.each(to_update, function(index, row){
                        var rec_id = $(row).data('id'),
                            record = list.records.get(rec_id);
                        if(!record || record.get(field_group)[0] != prev_group_id)return;

                        var vals = {};
                        vals[seqname] = seq;
                        fct(dataset, rec_id, vals);
                        $.when(record.set(seqname, seq)).then(function(){
                            list.set_node_member_attr(prev, $(list.$current.find('tr[data-id="'+rec_id+'"]')));
                        });
                        seq++;
                    });
                    var test=5;
                },
                setup_resequence_rows: function (list, dataset) {
                    var self = this;
                    self._super(list, dataset);
                    if(dataset.TreeGridMode){
                        list.$current.sortable('option', {
                            stop: function (event, ui) {
                                self.resequence_rows_stop(list,dataset,event,ui);
                            },
                            items: '> tr[data-id],tr[data-group_id]',
                        });
                        list.$current.find('tr[row_type="member"]').draggable('disable');
                    }
                },
            });
    instance.web.ListView.List
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
                        self.dataset.TreeGridMode = true;
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
                            QWeb.render('TreeGrid.add_group_options'));
                    }
                    else{
                        columns = self.view.columns;
                        options = self.view.options;
                        var columns = _(columns ).filter(function (column) {
                            return column.invisible !== '1';
                        }).length;
                        if (options.selectable) { columns++; }
                        if (options.deletable) { columns++; }
                        $.each(groups, function(index, group){
                            group_row = $(QWeb.render('TreeGrid.group_row',{
                                group: group,
                                colspan: columns,
                            }));
                            row_class = 'oe_group_level'+group.id;
                            if(group.parent_id){
                                parent_id = group.parent_id[0];
                                parent_row = self.$current.find('tr[row_type="group"][data-group_id="'+parent_id+'"]');
                                row_class = parent_row.attr('class') + ' ' + row_class;
                                group_row.addClass(row_class);
                                brother = self.$current.find('tr[parent_id="'+parent_id+'"]:last');
                                if(!brother.size()){
                                    group_row.insertAfter(self.$current.find('tr[data-group_id="'+parent_id+'"]:last'));
                                }
                                else{
                                    group_row.insertAfter(self.$current.find('tr[data-group_id="'+brother.attr("data-group_id")+'"]:last'));
                                }
                            }
                            else{
                                group_row.addClass(row_class);
                                self.$current.prepend(group_row);
                            }

                            vision_controller = self.$current.find('i#vision_controller'+group.id);
                            vision_controller.addClass(row_class);
                            self.init_group_options(group_row);
                            self.init_vision_controller(group_row, vision_controller);

                            curr_last = group_row;
                            $.each(group.members_ids, function(index, id){
                                curr = self.$current.find('tr[data-id='+id+']');
                                self.set_node_member_attr(group_row, curr);
                                curr.insertAfter(curr_last);
                                curr_last = curr;
                            });
                        });
                    }
                },
                set_node_member_attr: function(row, member_row){
                    member_row.attr('level', row.attr("level"));
                    member_row.attr('row_type', 'member');
                    member_row.attr('data-group_id', row.data("group_id"));
                    member_row.addClass(row.attr('class'));
                },
                init_group_options: function(row){
                    var self = this,
                        add_members_class = '.fa-plus',
                        add_group_class = '.fa-plus-circle',
                        remove_group_class = '.fa-trash-o';

                    if (self.view.is_action_enabled('create') && !self.is_readonly()) {
                        var columns = _(self.columns).filter(function (column) {
                            return column.invisible !== '1';
                        }).length;
                        if (self.options.selectable) { columns++; }
                        if (self.options.deletable) { columns++; }

                        var $options = $(QWeb.render('TreeGrid.group_options'));

                        // add members
                        $options.find(add_members_class)
                            .bind('click', function(e){
                                e.preventDefault();
                                e.stopPropagation();
                                if (self.view.editor.form.__blur_timeout) {
                                    clearTimeout(self.view.editor.form.__blur_timeout);
                                    self.view.editor.form.__blur_timeout = false;
                                }
                                self.view.ensure_saved().done(function () {
                                    row_id = row.attr("data-group_id");
                                    self.dataset.context.__contexts.push("{'default_abstract_group_id':"+row_id+"}");
                                    self.view.do_add_record();
                                    buffer_row = self.$current.find('tr[data-id="false"]')
                                    target_row = self.$current.find('tr[data-group_id="'+row_id+'"]:last');
                                    buffer_row.insertAfter(target_row);
                                });
                            });
                        row.find('th').append($options);
                    }
                    //and then remove the native "add an item"
                    self.$current.find('.oe_form_field_one2many_list_row_add').remove();
                },
                init_vision_controller: function(row, el){
                    var self = this;
                    el.bind('click', function(event){
                        vision_controller = $(event.target);
                        row_class = 'oe_group_level' + row.attr('data-group_id');

                        if(vision_controller.hasClass('fa-arrow-right')){
                            // show only the same level elements
                            vision_controller
                                                .removeClass('fa-arrow-right')
                                                .addClass('fa-arrow-down');
                            row_level = row.attr('level');
                            group_level = parseInt(row_level) + 1;
                            elements = self.$current
                                                    .find('tr[row_type="member"][level="'+row_level+'"].'+
                                                          row_class + ',' + 'tr[row_type="group"][level="'+ 
                                                          group_level+'"].' + row_class);
                            elements.removeClass('hidden');
                        }
                        else{
                            // hide all sub-level
                            self.$current.find('i.'+row_class)
                                                                .removeClass('fa-arrow-down')
                                                                .addClass('fa-arrow-right');
                            elements = self.$current
                                .find('tr.'+row_class)
                                .not(self.$current.find('tr[row_type="group"][data-group_id="'+row.attr('data-group_id')+'"]'));
                            elements.addClass('hidden');
                        }
                    });
                },
            });
}