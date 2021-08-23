/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('pos_account_wallet_coupon.Order', function (require) {
    "use strict";
    var PosModels = require('point_of_sale.models');
    var Order = PosModels.Order;

    PosModels.Order = Order.extend({
        get_paymentline: function(cid){
            var paymentlines = this.paymentlines.models;
            for(var i = 0; i < paymentlines.length; i++){
                if(paymentlines[i].cid === cid){
                    return paymentlines[i];
                }
            }
            return null;
        },
    });
});
