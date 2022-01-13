/*
    © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define("pos_account_wallet_coupon.PaymentLineWallet", function (require) {
    "use strict";

    var core = require("web.core");
    var utils = require("web.utils");
    const {Gui} = require("point_of_sale.Gui");
    var models = require("point_of_sale.models");

    var _t = core._t;
    var round_di = utils.round_decimals;
    // Add information relative to cagnotte on payment line
    var _payment_line_proto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function () {
            var self = this;
            // TODO:
            // self.no_negative = false;
            self.account_wallet_id = false;
            self.wallet_balance = 0;
            self.wallet_code = "";
            return _payment_line_proto.initialize.apply(this, arguments);
        },
        async add_coupon(code) {
            this._check_coupon_is_usable(code);

            await this._get_coupon_values(code);
        },
        _check_coupon_is_usable(code) {
            var plines = this.order.paymentlines.models;
            var pline = false;
            for (var i = 0; i < plines.length; i++) {
                pline = plines[i];
                if (pline.has_cagnotte()) {
                    if (pline.get_wallet_code() === code) {
                        Gui.showPopup("ErrorPopup", {
                            title: _t("Coupon not reusable"),
                            body: _t(
                                "The coupon code " +
                                    code +
                                    " is already use in this order."
                            ),
                        });
                        return;
                    }
                }
            }
        },
        _add_balance_wallet_domain(domain) {
            domain.push(["balance", ">", 0]);
        },
        _get_wallet_domain(code) {
            var client = this.order.get_client();
            var client_id = false;
            if (client !== null) {
                client_id = client.id;
            }
            var domain = [
                ["coupon_id.code", "=", code],
                [
                    "wallet_type_id.journal_id",
                    "=",
                    this.payment_method.cash_journal_id[0],
                ],
                "|",
                ["partner_id", "=", false],
                ["partner_id", "=", client_id],
            ];
            this._add_balance_wallet_domain(domain, code);
            return domain;
        },
        _get_wallet_fields() {
            // TODO: Add no_negative
            return ["balance", "coupon_id"];
        },
        _get_coupon_values(code) {
            var self = this;
            var domain = this._get_wallet_domain(code);
            var fields = this._get_wallet_fields();
            var payment_method = this.payment_method;
            return new Promise(function () {
                self.order.pos
                    .rpc({
                        model: "account.wallet",
                        method: "search_read",
                        args: [domain, fields],
                    })
                    .then(function (wallet) {
                        if (wallet.length) {
                            self.set_wallet(wallet[0]);
                        } else {
                            Gui.showPopup("ErrorPopup", {
                                title: _t("Wallet not usable"),
                                body: _t(
                                    "The wallet code " +
                                        code +
                                        " is not usable" +
                                        ". Check payment method : " +
                                        payment_method.name +
                                        ". Check customer"
                                ),
                            });
                            return;
                        }
                    });
            });
        },
        // Sets the account_cagnotte_id on this payment line
        set_wallet: function (wallet) {
            var self = this;
            self.account_wallet_id = wallet.id;
            // TODO:
            // self.no_negative = coupon.no_negative;
            self.wallet_balance = round_di(
                parseFloat(wallet.balance) || 0,
                self.pos.currency.decimals
            );
            if (wallet.balance <= 0) {
                wallet.balance = self.get_amount();
            }
            self.wallet_code = wallet.coupon_id[1];
            self.set_amount(
                Math.min(
                    wallet.balance.toFixed(self.pos.currency.decimals),
                    self.pos.get_order().get_due(self)
                )
            );
        },
        // Returns the coupon on this paymentline
        get_wallet() {
            return this.account_wallet_id;
        },
        get_wallet_code() {
            return this.wallet_code;
        },
        get_wallet_balance() {
            return this.wallet_balance;
        },
        // Returns the flag has_cagnotte from journal
        has_cagnotte() {
            return this.payment_method.is_wallet_with_coupon;
        },
        // Returns the flag has_cagnotte from cagnotte
        check_cagnotte_amount() {
            // TODO:
            // return this.no_negative;
            return false;
        },

        init_from_JSON(json) {
            var self = this;
            _payment_line_proto.init_from_JSON.call(this, json);
            self.account_wallet_id = json.account_wallet_id;
            self.wallet_code = json.wallet_code;
        },

        export_as_JSON() {
            var self = this;
            var json_repr = _payment_line_proto.export_as_JSON.call(this, arguments);
            json_repr.account_wallet_id = self.get_wallet();
            json_repr.wallet_code = self.get_wallet_code();
            json_repr.wallet_balance = self.get_wallet_balance();
            return json_repr;
        },
        export_for_printing() {
            var self = this;
            var json_repr = _payment_line_proto.export_for_printing.call(
                this,
                arguments
            );
            json_repr.account_wallet_id = self.get_wallet();
            json_repr.wallet_code = self.get_wallet_code();
            json_repr.wallet_balance = self.get_wallet_balance();
            return json_repr;
        },
    });
    return models;
});
