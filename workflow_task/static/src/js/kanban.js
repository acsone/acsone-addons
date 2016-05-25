odoo.define('workflow_task', function (require) {
"use strict";
    
var common = require('web.form_common');
var utils = require('web.utils');
var core = require('web.core');
var Model = require('web.DataModel');
var session = require('web.session');
var KanbanRecord = require('web_kanban.Record');

var KanbanView = require('web_kanban.KanbanView');

KanbanView.include({
    reload_record: function (event) {
        this._super(event);
        var self = this;
        if (self.x2m != 'undefined' && self.x2m.dataset.ids.length > 0 && self.x2m.options.reload_on_button) {
            var parent_form = self.x2m.view;
            $.when().then(function () {
                if (parent_form)
                    return parent_form.save();
                else
                    return $.when();
            }).done(function () {
                self.x2m.view.reload();
            });
        }
    },
});
});
