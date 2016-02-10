openerp.workflow_activity_action = function(instance) {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

instance.web.form.widgets.add('many2many_action_buttons',
        'instance.web.form.FieldMany2ManyActionButtons');

instance.web.form.FieldMany2ManyActionButtons = instance.web.form.AbstractField.extend(instance.web.form.CompletionFieldMixin, instance.web.form.ReinitializeFieldMixin, {
    template: "FieldMany2ManyActionButtons",
    button_template: "FieldMany2ManyActionButton",
    init: function() {
        this._super.apply(this, arguments);
        instance.web.form.CompletionFieldMixin.init.call(this);
        this.set({"value": []});
        this._display_orderer = new instance.web.DropMisordered();
        this._drop_shown = false;
    },
    get_render_data: function(ids){
        var self = this;
        var dataset = new instance.web.DataSetStatic(this, this.field.relation, self.build_context());
        return dataset.name_get(ids);
    },
    render_button: function(data) {
        var self = this;
        var parent = this;
        buttons = QWeb.render(self.button_template, {elements: data})
        self.$el.html(buttons);
        parent_data = data
        $('button', self.$el).each(function(el) {
            parent_el = el
            $(this).click(function(){
                parent_form = self.view
                button = this
                $.when().then(function () {
                    if (parent_form) {
                        parent_form.save();
                        var context = self.view.dataset.context;
                        context['res_type'] = self.view.model;
                        context['res_id'] = self.view.datarecord.id;
                        var model = new openerp.Model(openerp.session, self.field.relation);
                        model.call("do_action", [parseInt(button.dataset.id)], {"context": context}).then(function(result) {
                            self.view.do_action(result)
                            self.view.reload();
                        });
                    } else {
                        return $.when();
                    }
                });
            });
        });
    },
    render_value: function() {
        var self = this;
        var dataset = new instance.web.DataSetStatic(this, this.field.relation, self.build_context());
        var values = self.get("value");
        var handle_names = function(data) {
            if (self.isDestroyed())
                return;
            var indexed = {};
            _.each(data, function(el) {
                indexed[el[0]] = el;
            });
            data = _.map(values, function(el) { return indexed[el]; });
            self.render_button(data);
        }
        if (! values || values.length > 0) {
            return this._display_orderer.add(self.get_render_data(values)).done(handle_names);
        } else {
            handle_names([]);
        }
    },
});

};
