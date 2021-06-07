/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('pos_cagnotte_coupon.models', function (require) {
"use strict";

    var core = require('web.core');
    var utils = require('web.utils');

    var _t = core._t;
    var round_di = utils.round_decimals;

    var PosModels = require('point_of_sale.models');

    var PosModel = PosModels.PosModel;
    var PosModelSuper = PosModel.prototype;

    var OrderLine = PosModels.Orderline;
    var OrderLineSuper = OrderLine.prototype;

    var PaymentLine = PosModels.Paymentline;
    var PaymentLineSuper = PaymentLine.prototype;

    // add has_cagnotte flag on product to avoid merge on it

    PosModels.PosModel = PosModel.extend({
        initialize: function(session, attributes) {
            var self = this;
            self.add_fields_to_read();
            return PosModelSuper.initialize.call(self, session, attributes);
        },

        get_fields_to_add_by_model: function() {
            return {
                'product.product': [
                    'has_cagnotte'
                ],
                'account.journal': [
                    'has_cagnotte', 'check_cagnotte_amount',
                ],

            }
        },

        add_fields_to_read: function() {
            // Add fields to read
            var self = this;
            var fields_by_model = self.get_fields_to_add_by_model();

            var model, model_name, fields_to_add;
            for (var i = 0 ; i < self.models.length; i++) {
                model = self.models[i];
                model_name = model.model;

                if (model_name in fields_by_model) {
                    fields_to_add = fields_by_model[model_name];
                    _.each(fields_to_add, function(field_name) {
                        if (model.fields.indexOf(field_name) === -1) {
                            model.fields.push(field_name);
                        }
                    });
                }
            }
        }
    });

    PosModels.Orderline = OrderLine.extend({
        initialize: function(session, attributes) {
            var self = this;
            self.coupon_code = false;
            return OrderLineSuper.initialize.call(self, session, attributes);
        },

        // returns the flag has_cagnotte from product
        has_cagnotte: function() {
            var self = this;
            return self.product.has_cagnotte;
        },

        // we do not merge line with cagnotte
        can_be_merged_with: function(orderline){
            var self = this;
            if (self.has_cagnotte()) {
                return false;
            } else {
                return OrderLineSuper.can_be_merged_with.call(self, orderline);
            }
        },

        // Generates a public identification number for the coupon.
        generateUniqueId: function(base) {
            var self = this;
            var d = new Date().getTime();
            if(window.performance && typeof window.performance.now === "function"){
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxxxxxx'.replace(/[x]/g, function(c) {
                var r = (d + Math.random() * 10) % 10 | 0;
                d = Math.floor(d / 10);
                return (r).toString(10);
            });
            return uuid + base;
        },

        // returns the coupon on this orderline
        get_coupon_code: function() {
            var self = this;
            if (self.has_cagnotte()) {
                if (self.has_cagnotte()) {
                    if (!self.coupon_code) {
                        self.coupon_code = self.generateUniqueId(self.pos.pos_session.id);
                    }
                    return self.coupon_code;
                }
            }
            return false;
        },

        export_as_JSON: function() {
            var self = this;
            var json_repr = OrderLineSuper.export_as_JSON.call(self, arguments);
            json_repr.coupon_code = self.get_coupon_code();
            return json_repr;
        },

        export_for_printing: function() {
            var self = this;
            var json_repr = OrderLineSuper.export_for_printing.call(self, arguments);
            json_repr.coupon_code = self.get_coupon_code();
            return json_repr;
        }
    });

    // Add information relative to cagnotte on payment line
    PosModels.Paymentline = PaymentLine.extend({
        initialize: function(attributes, options) {
            var self = this;
            self.no_negative = false;
            self.account_cagnotte_id = false;
            self.solde_cagnotte = 0;
            self.coupon_code = '';
            return PaymentLineSuper.initialize.call(self, attributes, options);
        },

        //sets the account_cagnotte_id on this payment line
        set_coupon: function(coupon){
            var self = this;
            self.account_cagnotte_id = coupon.id;
            self.no_negative = coupon.no_negative;
            self.solde_cagnotte = round_di(parseFloat(coupon.solde_cagnotte) || 0, self.pos.currency.decimals);
            if (coupon.solde_cagnotte <= 0){
                coupon.solde_cagnotte = self.get_amount();
            }
            self.coupon_code = coupon.coupon_code;
            self.set_amount(Math.min(coupon.solde_cagnotte.toFixed(self.pos.currency.decimals), self.pos.get_order().get_due(self)));
        },

        // returns the coupon on this paymentline
        get_coupon: function() {
            return this.account_cagnotte_id;
        },

        get_coupon_code: function() {
            return this.coupon_code;
        },

        get_solde_cagnotte: function() {
            return this.solde_cagnotte;
        },

        // returns the flag has_cagnotte from journal
        has_cagnotte: function() {
            return this.cashregister.journal.has_cagnotte;
        },

        // returns the flag has_cagnotte from cagnotte
        check_cagnotte_amount: function() {
            return this.no_negative;
        },

        init_from_JSON: function(json) {
            var self = this;
            PaymentLineSuper.init_from_JSON.call(self, json);
            self.account_cagnotte_id = json.account_cagnotte_id;
        },

        export_as_JSON: function() {
            var self = this;
            var json_repr = PaymentLineSuper.export_as_JSON.call(self, arguments);
            json_repr.account_cagnotte_id = self.get_coupon();
            return json_repr;
        },

        export_for_printing: function() {
            var self = this;
            var json_repr = PaymentLineSuper.export_for_printing.call(self, arguments);
            json_repr.account_cagnotte_id = self.get_coupon();
            return json_repr;
        }

    });

});
