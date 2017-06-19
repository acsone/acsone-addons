odoo.define('pos_cagnotte_coupon.screens', function (require) {
"use strict";

    var core = require('web.core');
    var _t = core._t;

    var PosScreens = require('point_of_sale.screens');
    var PaymentScreenWidget = PosScreens.PaymentScreenWidget;

    PaymentScreenWidget.include({

        init: function() {
            var self = this;
            self._super.apply(self, arguments);

            var keyboard_handler = self.keyboard_handler;
            var keyboard_keydown_handler = self.keyboard_keydown_handler;

            // Very dirty but all keydown/keypress events are overriden
            // when payment screen is shown
            self.keyboard_handler = function(event) {
                if(self.allow_custom_keyboard_handler(event)) {
                    keyboard_handler(event)
                }
            };
            self.keyboard_keydown_handler = function(event) {
                if(self.allow_custom_keyboard_handler(event)) {
                    keyboard_keydown_handler(event)
                }
            };
        },

        allow_custom_keyboard_handler: function(event) {
            /*
            If coupon popup is open and if current target is the payment
            coupon code input, we don't allow the custom keyboard handler.
             */
            var self = this;
            var allow = true;
            if (self.is_coupon_dialog_open()) {
                allow = !$(event.target).is('input.payment-coupon-code');
            }
            return allow;
        },

        is_coupon_dialog_open: function() {
            return !$('div.set-coupon-code-dialog').hasClass('oe_hidden');
        },

        // Add behavior on Set coupon Code button on payment line
        render_paymentlines: function(){
            var self = this;
            self._super.apply(self, arguments);

            self.$('.paymentlines-container .set-coupon-code').click(function() {
                var $button = $(this);
                var line_id = $button.data('cid');
                self.gui.show_popup('set-coupon-code', {
                    line: self.get_payment_line_by_id(line_id),
                    payment_screen: self,
                });
            });
        },

        get_payment_line_by_id: function(line_id) {
            var self = this;
            var currentOrder = self.pos.get_order();
            var plines = currentOrder.paymentlines.models;
            var line;
            for(var i=0; i < plines.length; i++) {
                line = plines[i];
                if(line_id === line.cid) {
                    return line;
                }
            }
            return false;
        },

        validate_order: function(force_validation) {
            var self = this;

            var currentOrder = self.pos.get('selectedOrder');
            var plines = currentOrder.paymentlines.models;
            var pline;
            for (var i = 0; i < plines.length; i++) {
                pline = plines[i];
                // check cagnotte have coupon attached
                if (pline.has_cagnotte()){
                    if (!pline.get_coupon()) {
                        self.gui.show_popup('error', {
                            'title': _t('Cagnotte without coupon'),
                            'body': _t('You cannot use cagnotte without a coupon.'),
                        });
                        return;
                    }
                    if (pline.check_cagnotte_amount()){
                        if (pline.get_amount() > pline.get_solde_cagnotte()) {
                            self.gui.show_popup('error',{
                                'title': _t('Cagnotte with too big amount'),
                                'body': _t('You cannot use cagnotte with amount too big.'),
                            });
                            return;
                        }
                    }
                }
            }
            self._super();
        },

    });

});