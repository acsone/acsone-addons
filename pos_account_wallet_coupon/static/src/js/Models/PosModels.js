/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define("pos_account_wallet_coupon.PosModels", function (require) {
    "use strict";

    var PosModels = require("point_of_sale.models");
    var PosModel = PosModels.PosModel;
    var PosModelSuper = PosModel.prototype;

    // Add has_cagnotte flag on product to avoid merge on it

    PosModels.PosModel = PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
            self.add_fields_to_read();
            return PosModelSuper.initialize.call(self, session, attributes);
        },

        get_fields_to_add_by_model: function () {
            return {
                "product.product": ["is_wallet_with_coupon"],
                "pos.payment.method": ["is_wallet_with_coupon", "cash_journal_id"],
                "account.journal": ["is_wallet_with_coupon", "check_cagnotte_amount"],
            };
        },

        add_fields_to_read: function () {
            // Add fields to read
            var self = this;
            var fields_by_model = self.get_fields_to_add_by_model();

            var model = false;
            var model_name = false;
            var fields_to_add = false;
            for (var i = 0; i < self.models.length; i++) {
                model = self.models[i];
                model_name = model.model;

                if (model_name in fields_by_model) {
                    fields_to_add = fields_by_model[model_name];
                    _.each(fields_to_add, function (field_name) {
                        if (model.fields.indexOf(field_name) === -1) {
                            model.fields.push(field_name);
                        }
                    });
                }
            }
        },
    });
});
