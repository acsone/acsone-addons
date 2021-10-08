/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/
odoo.define("pos_account_wallet_coupon.Orderline", function (require) {
    "use strict";
    var PosModels = require("point_of_sale.models");
    var OrderLine = PosModels.Orderline;
    var OrderLineSuper = OrderLine.prototype;

    PosModels.Orderline = OrderLine.extend({
        initialize: function (session, attributes) {
            var self = this;
            self.coupon_code = false;
            return OrderLineSuper.initialize.call(self, session, attributes);
        },

        // Returns the flag has_cagnotte from product
        has_cagnotte: function () {
            var self = this;
            return self.product.is_wallet_with_coupon;
        },

        // We do not merge line with cagnotte
        can_be_merged_with: function (orderline) {
            var self = this;
            if (self.has_cagnotte()) {
                return false;
            }
            return OrderLineSuper.can_be_merged_with.call(self, orderline);
        },

        // Generates a public identification number for the coupon.
        generateUniqueId: function (base) {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                // Use high-precision timer if available
                d += performance.now();
            }
            var uuid = "xxxxxxxxxxxx".replace(/[x]/g, function () {
                var r = (d + Math.random() * 10) % 10 | 0;
                d = Math.floor(d / 10);
                return r.toString(10);
            });
            return uuid + base;
        },

        // Returns the coupon on this orderline
        get_coupon_code: function () {
            var self = this;
            if (self.has_cagnotte()) {
                if (self.has_cagnotte()) {
                    if (!self.coupon_code) {
                        self.coupon_code = self.generateUniqueId(
                            self.pos.pos_session.id
                        );
                    }
                    return self.coupon_code;
                }
            }
            return false;
        },

        export_as_JSON: function () {
            var self = this;
            var json_repr = OrderLineSuper.export_as_JSON.call(self, arguments);
            json_repr.coupon_code = self.get_coupon_code();
            return json_repr;
        },

        export_for_printing: function () {
            var self = this;
            var json_repr = OrderLineSuper.export_for_printing.call(self, arguments);
            json_repr.coupon_code = self.get_coupon_code();
            return json_repr;
        },
    });
});
