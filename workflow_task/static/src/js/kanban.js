odoo.define('workflow_task', function (require) {
"use strict";
    
var common = require('web.form_common');
var utils = require('web.utils');
var core = require('web.core');
var Model = require('web.DataModel');
var session = require('web.session');
var KanbanRecord = require('web_kanban.Record');

KanbanRecord.include({
    do_reload: function() {
        res = this._super();
        var self = this;
        if (self.view.m2m != 'undefined' && self.view.m2m.dataset.ids.length > 0 && self.view.m2m.options.reload_on_button) {
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
});
