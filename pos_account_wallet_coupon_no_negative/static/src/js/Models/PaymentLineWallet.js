/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('pos_account_wallet_coupon_no_negative.PaymentLineWallet', function (require) {
    "use strict";
    
    //var models = require('pos_account_wallet_coupon.PaymentLineWallet');
    var models = require('pos_account_wallet_coupon.PaymentLineWallet');

    // Add information relative to cagnotte on payment line
    var _payment_line_proto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function(){
            var self = this;
            self.no_negative = false;
            return _payment_line_proto.initialize.apply(this, arguments);
        },
        _get_balance_wallet_domain(){
            return '|', ['no_negative', '=', false], ['balance', '>', 0];
        },
        _get_wallet_fields(){
            // TODO: Add no_negative
            var self = this;
            var res = _payment_line_proto._get_wallet_fields.apply(this);
            res.push('no_negative');
            return res
        },
        //sets the account_cagnotte_id on this payment line
        set_wallet: function(wallet){
            var self = this;
            self.no_negative = wallet.no_negative;
            return _payment_line_proto.set_wallet.call(this, wallet);
        },

        // returns the flag has_cagnotte from cagnotte
        check_cagnotte_amount() {
            return this.no_negative;
        },
    });
    return models;
});
    