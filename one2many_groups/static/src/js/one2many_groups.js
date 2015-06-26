openerp.one2many_groups = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt, QWeb = instance.web.qweb;
    GridTriggerKey = 'TreeGrid';

    instance.web.form.FormWidget
            .include({
                build_context: function() {
                    res = this._super.apply(this, arguments);
                    if(this.dataset && this.dataset.TreeGridMode && this.dataset.dynamic_context){
                        res.add(this.dataset.dynamic_context)
                    }
                    return res;
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
                        seqname = self.get_seqname(),
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
                        var group_name = list.$current
                                                    .find('tr[row_type="group"][data-group_id="'+prev_group_id+'"]')
                                                                                                                    .text()
                                                                                                                    .trim();
                        curr_record.set(field_group, [prev_group_id, group_name]);
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
                        record.set(seqname, seq);
                        seq++;
                    });
                },
                setup_resequence_rows: function (list, dataset) {
                    var self = this;
                    self._super(list, dataset);
                    if(dataset.TreeGridMode){
                        list.$current.sortable('option', {
                            stop: function (event, ui) {
                                self.resequence_rows_stop(list,dataset,event,ui);
                            },
                            items: '> tr[data-id],tr:not(tr[data-group_id]:first())[data-group_id]',
                            cancel:'tr[row_type="group"]',
                        });
                    }
                },
            });
    instance.web.ListView.List
            .include({
                group_fields : [ 'name', 'sequence', 'parent_id',
                        'members_ids', 'children_ids', 'master_id', 'level' ],
                add_members_class : '.fa-plus',
                add_group_class : '.fa-plus-circle',
                remove_group_class : '.fa-trash-o',

                init : function(parent, dataset, view_id, options) {
                    res = this._super(parent, dataset, view_id, options);
                    return res;
                },
                start : function() {
                    res = this._super.apply(this, arguments);
                    return res;
                },
                render : function() {
                    var self = this,
                        res = self._super.apply(this, arguments),
                        context = openerp.web.pyeval.eval('contexts', self.dataset.context);
                    if (GridTriggerKey in context && context[GridTriggerKey]) {
                        self.dataset.TreeGridMode = true;
                        self.dataset
                            .call('get_cls_group')
                            .done(function(result){
                                domain = [['master_id', '=', self.dataset.parent_view.datarecord.id]];
                                self.dataset.TreeGridInstance = new instance.web.Model(result, self.dataset.context);
                                self.dataset.TreeGridInstance
                                    .call('search_read', [domain,self.group_fields])
                                    .done(function(result){
                                        self.setup_groups_view(result);
                                    });
                            });
                    }
                    return res;
                },
                render_record: function (record) {
                    var self = this,
                        res = self._super(record);
                    if(self.dataset.TreeGridMode){
                        var group_id = record.get('abstract_group_id'),
                            group_row = self.$current.find('tr[row_type="group"][data-group_id="'+group_id+'"]'),
                            member_row = $(res);
                        self.set_node_member_attr(group_row, member_row);
                        return member_row.prop('outerHTML');
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
                        self.init_new_members();
                    }
                    self.$current.find('i.fa-plus-circle').bind("click", function(){
                        var group_manager_form = $(QWeb.render('TreeGrid.create_group')),
                            switch_map = {
                                true: _t('Create'),
                                false: _t('Edit'),
                            },
                            group_name = group_manager_form.find("input[name='group_name']"),
                            curr_name = self.$current.find('tr[row_type="group"][data-group_id="'+group_id+'"]').text().trim(),
                            group_id = $(this.parentElement).data('group_id'),
                            checkbox_mode = group_manager_form.find("[name='checkbox_mode']");
                        checkbox_mode.bootstrapSwitch({
                            onText: switch_map[true],
                            offText: switch_map[false],
                            state: true,
                            size: 'small',
                            animate: true,
                            onSwitchChange: function(event, state){
                                if(state){
                                    group_name.val('');
                                    checkbox_mode.attr('checked', true);
                                }
                                else{
                                    group_name.val(curr_name);
                                    checkbox_mode.attr('checked', false);
                                }
                            },
                            onInit: function(event, state){
                                checkbox_mode.attr('checked', true);
                             }
                        });
                        group_manager_form.dialog({
                            buttons: [{
                                text: "Save",
                                click: function(){
                                    var dialog = $(this);
                                    if(checkbox_mode.prop('checked')){
                                        vals  ={
                                            parent_id: group_id,
                                            name: group_name.val(),
                                            master_id: self.dataset.parent_view.datarecord.id,
                                        }
                                        self.dataset.TreeGridInstance
                                            .call('create', [vals])
                                            .done(function(result){
                                                self.render();
                                                $(dialog).dialog("close");
                                            });
                                    }
                                },
                            }],
                            modal:true,
                            width:580,
                            height:260,
                        });
                    });
                },
                init_new_members: function(){
                    var self = this;
                    if (self.view.is_action_enabled('create') && !self.is_readonly()) {
                        new_members = self.$current.find('tr[data-id*="one2many_v_id"]');
                        if(new_members.length){
                            $.each(new_members, function(index, member){
                                var member = $(member),
                                    member_record = self.records.get(member.data('id')),
                                    group_id = member_record.get('abstract_group_id')[0],
                                    last_group_row = self.$current.find('tr[data-group_id="'+group_id+'"]:last');
                                self.set_node_member_attr(last_group_row, member);
                                member.insertAfter(last_group_row);
                            });
                        }
                    }
                },
                set_node_member_attr: function(row, member_row){
                    member_row.attr('level', row.attr("level"));
                    member_row.attr('row_type', 'member');
                    member_row.attr('data-group_id', row.data("group_id"));
                    member_row.addClass(row.attr('class'));
                },
                init_group_options: function(row){
                    var self = this;

                    if (self.view.is_action_enabled('create') && !self.is_readonly()) {
                        var columns = _(self.columns).filter(function (column) {
                            return column.invisible !== '1';
                        }).length;
                        if (self.options.selectable) { columns++; }
                        if (self.options.deletable) { columns++; }

                        var $options = $(QWeb.render('TreeGrid.group_options', {
                            group_id: row.data('group_id'),
                        }));

                        // add members
                        $options.find(self.add_members_class)
                            .bind('click', function(e){
                                e.preventDefault();
                                e.stopPropagation();
                                if (self.view.editor.form.__blur_timeout) {
                                    clearTimeout(self.view.editor.form.__blur_timeout);
                                    self.view.editor.form.__blur_timeout = false;
                                }
                                self.view.ensure_saved().done(function () {
                                    row_id = row.attr("data-group_id");
                                    self.dataset.dynamic_context = "{'default_abstract_group_id':"+row_id+"}";
                                    self.view.do_add_record();
                                    buffer_row = self.$current.find('tr[data-id="false"]');
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