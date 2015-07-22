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
                        seq = prev.data('id') ? list.records.get(prev_id).get(seqname) + 1 : 1,
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
                show_fields: [],
                add_members_class : '.fa-plus',
                edit_group_class : '.fa-cog',
                add_group_class : '.fa-plus-circle',
                remove_group_class : '.fa-trash-o',
                hide_history_group_ids : [],

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
                        parent_view = self.dataset.parent_view,
                        parent_dataset = parent_view && parent_view.dataset,
                        context = parent_dataset && openerp.web.pyeval.eval('contexts', parent_dataset.context);
                    if (context && GridTriggerKey in context && context[GridTriggerKey] == self.dataset.child_name) {
                        self.dataset.TreeGridMode = true;
                        self.dataset
                            .call('get_cls_group')
                            .done(function(result){
                                domain = [['master_id', '=', self.dataset.parent_view.datarecord.id]];
                                self.dataset.TreeGridInstance = new instance.web.Model(result, self.dataset.context);
                                self.dataset.TreeGridInstance
                                                .call('get_complementary_fields')
                                                .done(function(result){
                                                    if(result.length){
                                                        self.show_fields = $.unique($.merge(self.show_fields, result));
                                                        self.group_fields = $.merge(self.group_fields, self.show_fields );
                                                    }
                                                    self.dataset.TreeGridInstance
                                                            .call('search_read', [domain,self.group_fields])
                                                            .done(function(result){
                                                                self.setup_groups_view(result);
                                                            });
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
                            group_id = $.isArray(group_id) && group_id[0] || group_id,
                            $group_row = self.$current.find('tr[row_type="group"][data-group_id="'+group_id+'"]'),
                            $member_row = $(res);
                        if($group_row.length){
                            $member_row.find('td').eq(0).attr('colspan', 2);
                        }
                        self.set_node_member_attr($group_row, $member_row);
                        return $member_row.prop('outerHTML');
                    }
                    return res;
                },
                get_columns_number: function(){
                    var self = this;
                    columns = self.view.columns;
                    options = self.view.options;
                    var columns = _(columns ).filter(function (column) {
                        return column.invisible !== '1';
                    }).length;
                    if (options.selectable) { columns++; }
                    if (options.deletable) { columns++; }
                    return columns;
                },
                init_anchor_options: function(){
                    var self = this,
                        group_row = $(QWeb.render('TreeGrid.group_row',{
                            group: false,
                            colspan: columns,
                        })),
                        columns = self.get_columns_number();
                    self.init_group_options(group_row);
                    self.$current.prepend(group_row);
                },
                setup_groups_view: function(groups){
                    var self = this;
                    if(!groups.length && self.is_readonly()){
                        self.init_anchor_options();
                        self.view.$el
                                    .find('tr.oe_list_header_columns')
                                    .find('th').eq(0).attr('colspan', 1);
                    }
                    else if(groups.length){
                        var columns = self.get_columns_number(),
                            $other_rows = self.$current
                                                    .find('tr')
                                                    .not('[data-id]');
                        self.view.$el
                                    .find('tr.oe_list_header_columns')
                                    .find('th').eq(0).attr('colspan', 2);
                        $.each($other_rows, function(index, row){
                            $(row).find('td').eq(0).attr('colspan', 2);
                        });
                        $.each(groups, function(index, group){
                            group_row = $(QWeb.render('TreeGrid.group_row',{
                                group: group,
                            }));
                            for(var i=1;i<=columns;i++){
                                group_row.append('<th style="text-align:right"></th>');
                            }
                            $.each(self.show_fields, function(index, field){
                                localized_label = self.view.$el.find('tr.oe_list_header_columns').find('th[data-id="'+field+'"]');
                                field_value = self.group_format_value(group[field]);
                                // located index + 1 because of colspan
                                group_row.find('th').eq(localized_label.index()+1).text(field_value);
                            });
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
                                $curr = self.$current.find('tr[data-id='+id+']');
                                $curr.find('td').eq(0).attr('colspan', 2);
                                self.set_node_member_attr(group_row, $curr);
                                $curr.insertAfter(curr_last);
                                curr_last = $curr;
                            });
                        });
                        self.init_new_members();
                    }
                    self.init_group_manager();
                    self.restore_display_from_history();
                },
                group_format_value: function(value){
                    var descriptor = {
                        type: 'float'
                    }
                    return instance.web.format_value(value, descriptor);
                },
                get_level_class: function(group_id){
                    return 'oe_group_level'+group_id;
                },
                init_group_manager_checkbox: function($group_manager_form){
                    var $checkboxes = $group_manager_form.find('.mutuallyexclusive');
                    $checkboxes.click(function () {
                        var checkedState = $(this).attr('checked');
                        $group_manager_form.find('.mutuallyexclusive:checked').each(function () {
                            $(this).attr('checked', false);
                            $group_manager_form.find('select[name="'+$(this).attr('name')+'"]').addClass('hidden');
                        });
                        $(this).attr('checked', checkedState);
                        select_box = $group_manager_form.find('select[name="'+$(this).attr('name')+'"]');
                        if(!checkedState){
                            select_box.addClass('hidden');
                        }
                        else{
                            select_box.removeClass('hidden');
                        }
                    });
                },
                init_group_manager_selectbox: function($group_manager_form, group_id){
                    var self = this;
                    self.dataset.TreeGridInstance
                                    .call('get_move_group_ids', [group_id])
                                    .done(function(result){
                                        if(result.length){
                                            var group_sequence_ids = result[0][0],
                                                group_parent_ids = result[0][1],
                                                $select_box_seq_before =
                                                    $group_manager_form.find('select[name="group_sequence_before"]'),
                                                $select_box_seq_after =
                                                    $group_manager_form.find('select[name="group_sequence_after"]'),
                                                $select_box_parent =
                                                    $group_manager_form.find('select[name="group_parent"]');
                                            var init_select = function($select_box, groups, field){
                                                $.each(groups, function(index, group){
                                                    $select_box.append(
                                                        QWeb.render('TreeGrid.select_option',{
                                                            key_value: group[field],
                                                            group_name: group['display_name'],
                                                        })
                                                    );
                                                });
                                            };
                                            init_select($select_box_seq_before, group_sequence_ids, 'sequence');
                                            init_select($select_box_seq_after, group_sequence_ids, 'sequence');
                                            init_select($select_box_parent, group_parent_ids, 'id');
                                        }
                                    });
                },
                init_group_manager: function(){
                    var self = this;
                    self.$current.find('i.group_management').bind("click", function(event){
                        var $trigger_tag = $(event.target),
                            mode = $trigger_tag.data('mode');
                        var title = mode =='edit' && _t('Edit') || mode=='create' && _t('Create') || mode=='unlink' && _t('Unlink'),
                            title_button = mode =='edit' && _t('Save') || mode=='create' && _t('Create') || mode=='unlink' && _t('Unlink');
                        var group_id = $trigger_tag.data('group_id'),
                            $group_row = self.$current.find('tr[row_type="group"][data-group_id="'+group_id+'"]'),
                            class_level = self.get_level_class(group_id);
                        var $group_manager_form = $(QWeb.render('TreeGrid.group_manager_form', {
                                title:title,
                                mode:mode,
                            }));
                        var $name = $group_manager_form.find("input[name='group_name']");
                        self.init_group_manager_checkbox($group_manager_form);
                        self.init_group_manager_selectbox($group_manager_form, group_id);
                        if(mode=='edit'){
                            var curr_name = $group_row.find('th[data-id="name"]').text().trim();
                            $name.val(curr_name);
                        }
                        $group_manager_form.dialog({
                            buttons: [
                                {
                                    text: _t('Cancel'),
                                    click: function(){
                                        $(this).dialog("close");
                                    },
                                },
                                {
                                text: title_button,
                                click: function(){
                                    var $dialog_form = $(this)
                                    if(mode == 'unlink'){
                                        var $unlink_rows = self.$current.find('tr.'+class_level),
                                            $members_rows = self.$current.find('tr.'+class_level+'[row_type="member"]');
                                        self.dataset.TreeGridInstance
                                                        .call('unlink', [group_id])
                                                        .done(function(result){
                                                            self.dataset.parent_view.reload();
                                                            $dialog_form.dialog("close");
                                                        });
                                    }
                                    else{
                                        var group_name = $name.val();
                                        if(mode == 'create'){
                                            var vals = {
                                                parent_id: parseInt(group_id),
                                                name: group_name,
                                                master_id: self.dataset.parent_view.datarecord.id,
                                            }
                                            self.dataset.TreeGridInstance
                                                            .call('create', [vals])
                                                            .done(function(result){
                                                                self.render();
                                                                $dialog_form.dialog("close");
                                                            });
                                        }
                                        else if(mode == 'edit'){
                                            var $position_checkbox = $dialog_form.find('.mutuallyexclusive[checked]'),
                                                vals = {};
                                            if(curr_name != group_name){
                                                vals['name'] = group_name;
                                            }
                                            if($position_checkbox.length){
                                                var select_name = $position_checkbox.attr('name'),
                                                    field = $position_checkbox.data('key');
                                                vals[field] =
                                                    parseInt($dialog_form.find('select[name="'+select_name+'"]').val());
                                                if(field == 'sequence'){
                                                    vals[field] = select_name.indexOf('before')>=0 ? vals[field] -1 || 1 :
                                                        vals[field] +1;
                                                }
                                            }
                                            self.dataset.TreeGridInstance
                                                            .call('write', [group_id, vals])
                                                            .done(function(result){
                                                                self.render();
                                                                $dialog_form.dialog("close");
                                                            });
                                        }
                                    }
                                },
                            }],
                            modal: true,
                            width: 580,
                        });
                    });
                },
                restore_display_from_history: function(){
                    var self = this;
                    $.each(self.hide_history_group_ids, function(index, group_id){
                        self.hide_group_level(group_id);
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
                                    group_id = member_record.get('abstract_group_id'),
                                    group_id = $.isArray(group_id) && group_id[0] || group_id,
                                    last_group_row = self.$current.find('tr[data-group_id="'+group_id+'"]:last');
                                member.find('td').eq(0).attr('colspan', 2);
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
                    var self = this,
                        read_mode = self.is_readonly();
                    if (self.view.is_action_enabled('create')) {
                        var columns = _(self.columns).filter(function (column) {
                            return column.invisible !== '1';
                        }).length;
                        if (self.options.selectable) { columns++; }
                        if (self.options.deletable) { columns++; }

                        var $options = $(QWeb.render('TreeGrid.group_options', {
                            group_id: row.data('group_id'),
                            read_mode: read_mode,
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
                                    $buffer_row = self.$current.find('tr[data-id="false"]');
                                    $buffer_row.find('td').eq(0).attr('colspan', 2);
                                    $target_row = self.$current.find('tr[data-group_id="'+row_id+'"]:last');
                                    $buffer_row.insertAfter($target_row);
                                });
                            });
                        row.find('th.oe_group_name[data-id="name"]')
                                .find('i').after($options);
                    }
                    // and then remove the native "add an item"
                    self.$current.find('.oe_form_field_one2many_list_row_add').remove();
                },
                init_vision_controller: function(row, el){
                    var self = this;
                    el.bind('click', function(event){
                        vision_controller = $(event.target);
                        group_id = vision_controller.data('group_id');
                        level = vision_controller.attr('level');
                        row_class = 'oe_group_level' + group_id;

                        if(vision_controller.hasClass('fa-arrow-right')){
                            group_index = self.hide_history_group_ids.indexOf(group_id);
                            self.hide_history_group_ids.splice(group_index, 1);
                            // show only the same level elements
                            vision_controller
                                                .removeClass('fa-arrow-right')
                                                .addClass('fa-arrow-down');
                            row_level = level;
                            group_level = parseInt(row_level) + 1;
                            elements = self.$current
                                                    .find('tr[row_type="member"][level="'+row_level+'"].'+
                                                          row_class + ',' + 'tr[row_type="group"][level="'+ 
                                                          group_level+'"].' + row_class);
                            elements.removeClass('hidden');
                        }
                        else{
                            // hide all sub-level
                            children_group_rows = self.$current.find('tr.'+row_class+'[row_type="group"]');
                            $.each(children_group_rows, function(index, row){
                                curr_group_id = $(row).data("group_id");
                                self.hide_history_group_ids.push(curr_group_id)
                            });
                            self.hide_group_level(group_id);
                        }
                    });
                },
                hide_group_level: function(group_id){
                    var self = this,
                        row_class = 'oe_group_level'+group_id;
                    self.$current.find('i.'+row_class)
                                    .removeClass('fa-arrow-down')
                                    .addClass('fa-arrow-right');
                    elements = self.$current
                                        .find('tr.'+row_class)
                                        .not(self.$current.find('tr[row_type="group"][data-group_id="'+group_id+'"]'));
                    elements.addClass('hidden');
                },
            });
}