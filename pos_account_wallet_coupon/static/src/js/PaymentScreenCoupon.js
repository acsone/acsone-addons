odoo.define("pos_account_wallet_coupon.PaymentScreenCoupon", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const {useListener} = require("web.custom_hooks");
    const Registries = require("point_of_sale.Registries");
    const PaymentScreenCoupon = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                useListener("add-coupon-code", this.addCouponCode);
            }
            async addCouponCode({detail: cid}) {
                const {confirmed, payload: code} = await this.showPopup(
                    "SetCouponCodePopup",
                    {}
                );
                if (confirmed && code !== "") {
                    const order = this.env.pos.get_order();
                    var line = order.get_paymentline(cid.cid);
                    line.add_coupon(code);
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PaymentScreenCoupon);

    return PaymentScreen;
});
