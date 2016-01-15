odoo.define('workflow_activity_action', function (require) {
"use strict";
    
    var common = require('web.form_common');
    var utils = require('web.utils');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var session = require('web.session');
    var form_relational = require('web.form_relational');
    var data = require('web.data');
    var QWeb = core.qweb;

var FieldMany2ManyActionButtons = form_relational.AbstractManyField.extend(common.CompletionFieldMixin, common.ReinitializeFieldMixin, {
    template: "FieldMany2ManyActionButtons",
    button_template: "FieldMany2ManyActionButton",
    init: function() {
        this._super.apply(this, arguments);
        common.CompletionFieldMixin.init.call(this);
        this.set({"value": []});
        this._display_orderer = new utils.DropMisordered();
        this._drop_shown = false;
    },
    get_render_data: function(ids){
        var self = this;
        var dataset = new data.DataSetStatic(this, this.field.relation, self.build_context());
        return dataset.name_get(ids);
    },
    render_button: function(data) {
        var self = this;
        var parent = this;
        var buttons = QWeb.render(self.button_template, {elements: data})
        self.$el.html(buttons);
        var parent_data = data
        $('button', self.$el).each(function(el) {
            var parent_el = el
            $(this).click(function(){
                var parent_form = self.view
                var button = this
                $.when().then(function () {
                    if (parent_form) {
                        parent_form.save();
                        var context = self.view.dataset.context;
                        context['res_type'] = self.view.model;
                        context['res_id'] = self.view.datarecord.id;
                        var model = new Model(self.field.relation);
                        model.call("do_action", [parseInt(button.dataset.id)], {"context": context}).then(function() {
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
        var dataset = new data.DataSetStatic(this, this.field.relation, self.build_context());
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

core.form_widget_registry.add('many2many_action_buttons', FieldMany2ManyActionButtons)

});
