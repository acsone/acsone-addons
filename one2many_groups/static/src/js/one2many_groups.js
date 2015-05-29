openerp.one2many_groups = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt, QWeb = instance.web.qweb;
    GridTriggerKey = 'TreeGrid';

    instance.web.form.widgets.add('x2many_tree_grid',
            'instance.one2many_groups.TreeGrid');
    instance.one2many_groups.TreeGrid = instance.web.ListView.List
            .include({
                group_fields : [ 'name', 'sequence', 'parent_id',
                        'members_ids', 'children_ids', 'master_id' ],
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
                                        if(!result.length){
                                            self.$current.prepend(
                                                QWeb.render('TreeGrid.add_group'));
                                        }
                                    });
                            });
                    }
                    return res;
                },
            });
}