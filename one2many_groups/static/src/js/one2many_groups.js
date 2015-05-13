openerp.one2many_groups = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt, QWeb = instance.web.qweb;

    instance.web.form.widgets.add('x2many_tree_grid',
            'instance.one2many_groups.TreeGrid');
    instance.one2many_groups.TreeGrid = instance.web.form.FieldOne2Many
            .extend({
                template : 'TreeGrid',
                widget_class : 'oe_form_tree_grid',
                cls_group : false,
                dataset_group : false,
                group_fields : ['name', 'sequence', 'parent_id', 'members_ids', 'children_ids'],

                init : function(field_manager, node) {
                    return this._super.apply(this, arguments);
                },
                load_views : function(r) {
                    var self = this;
                    new instance.web.Model(self.dataset.model,
                        self.dataset.context).call('get_cls_group').done(
                        function(result) {
                            self.cls_group = result;
                            self.dataset_group = new instance.web.DataSet(
                                    this, self.cls_group);
                            self.load_tree_grid(r);
                        });
                },
                load_tree_grid : function(fields_view) {
                    var self = this;
                    var $so_id = self.getParent().datarecord.id;

                    self.dataset_group.read_slice(self.group_fields, {
                        "domain" : [[ 'master_id', '=', $so_id], ['parent_id', '=', false]]
                    }).done(function(records) {
                        if(!records.length){
                            self.$el.prepend(QWeb.render('group_options'));
                        }
                        else{
                            self.$el.find('table').append(QWeb.render(
                                    'TreeGrid.master_rows',{
                                        'group': records[0],
                                    }));
                            self.setup_view(self.$el.find('table'), records[0]);
                        }
                    });
                },
                setup_view : function(node, record){
                    var self = this;
                    _.each(record.members_ids, function(member){
                        node.append(QWeb.render('TreeGrid.members_rows'));
                    });
                    self.dataset_group.read_ids(record.children_ids, self.group_fields)
                        .done(function(records) {
                            _.each(records, function(child){
                                child_node = QWeb.render('TreeGrid.master_rows', {
                                    'group': child,
                                })
                                node.append(child_node);
                                self.setup_view(child_node, child);
                            });
                    });
                }
            });
}