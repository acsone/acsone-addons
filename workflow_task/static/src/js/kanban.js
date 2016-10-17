openerp.workflow_task = function(instance) {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

instance.web_kanban.KanbanRecord.include({

    do_reload: function() {
        res = this._super();
        var self = this;
        if (self.view.m2m !== undefined && self.view.m2m.dataset.ids.length > 0 && self.view.m2m.options.reload_on_button) {
            parent_form = self.view.m2m.view
            $.when().then(function () {
                if (parent_form)
                    return parent_form.save();
                else
                    return $.when();
            }).done(function () {
                self.view.m2m.view.reload();
            });
        }
        return res
    }
});
};
