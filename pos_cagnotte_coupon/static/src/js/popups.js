odoo.define('pos_cagnotte_coupon.popups', function (require) {
"use strict";

    var core = require('web.core');
    var Model = require('web.Model');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    var PopUpWidget = require('point_of_sale.popups');

    var SetCouponCodeWidget = PopUpWidget.extend({
        template:'SetCouponCodeWidget',
        events: {
            'click .close': 'close_popup',
            'click .validate-coupon': 'validate_coupon',
        },

        init: function() {
            var self = this;
            self._super.apply(self, arguments);
            self.ModelCagnotte = new Model('account.cagnotte');
        },

        close_popup: function() {
            var self = this;
            self.gui.close_popup();
        },

        validate_coupon: function() {
            var self = this;
            var coupon_code = self.get_coupon_value();
            var current_order = self.pos.get('selectedOrder');
            var client_id = self.get_client_id_from_order(current_order);
            var journal = self.line.cashregister.journal_id;
            var journal_id = journal[0];
            var journal_name = journal[1];

            var plines = current_order.paymentlines.models;
            var pline;
            for (var i = 0; i < plines.length; i++) {
                pline = plines[i];
                if (pline.has_cagnotte()) {
                    if (pline.get_coupon_code() === coupon_code) {
                        self.gui.show_popup('error',{
                            'title': _t('Coupon not reusable'),
                            'body': _t('The coupon code ' + coupon_code + ' is already use in this order.'),
                        });
                        return;
                    }
                }
            }

            self.ModelCagnotte.query(['solde_cagnotte', 'coupon_code', 'no_negative']).
                filter([['coupon_code','=', coupon_code],
                        ['cagnotte_type_id.journal_id', '=', journal_id,],
                        '|', ['cagnotte_type_id.no_negative', '=', false], ['solde_cagnotte', '>', 0],
                        '|', ['partner_id', '=', false], ['partner_id', '=', client_id]]).
                first().then(function(coupon) {
                    if (coupon){
                        var line = self.line;
                        if (line) {
                            line.set_coupon(coupon);
                            self.payment_screen.reset_input();
                            self.payment_screen.order_changes();
                            self.payment_screen.render_paymentlines();
                        }
                        self.close_popup();
                    } else {
                        self.gui.show_popup('error',{
                            'title': _t('Coupon not usable'),
                            'body': _t('The coupon code ' + coupon_code + ' is not usable' +
                                          '. Check payment method : ' + journal_name +
                                          '. Check customer'),
                        });
                        return;
                    }
            }, function (err, event) {
                event.preventDefault();
                self.gui.show_popup('error',{
                    title: _t('Impossible to check coupon'),
                    body: _t('Check your internet connection and try again.'),
                });
            });

        },

        get_client_id_from_order: function(order) {
            var self = this;
            var client = order.get_client();
            return !client ? false : client.id;
        },

        get_coupon_value: function() {
            var self = this;
            return self.$('input.payment-coupon-code').val();
        },

        show: function(options){
            var self = this;
            self.line = options.line;
            self.payment_screen = options.payment_screen;
            self._super.apply(self, arguments);
        },
    });

    gui.define_popup({name:'set-coupon-code', widget: SetCouponCodeWidget});

    return {
        SetCouponCodeWidget: SetCouponCodeWidget,
    }
});