odoo.define("pos_account_wallet_coupon.popups", function (require) {
    "use strict";
    var core = require("web.core");
    var _t = core._t;
    const TextInputPopup = require("point_of_sale.TextInputPopup");
    const Registries = require("point_of_sale.Registries");

    class SetCouponCodePopup extends TextInputPopup {}
    SetCouponCodePopup.template = "SetCouponCodePopup";
    SetCouponCodePopup.defaultProps = {
        confirmText: "Ok",
        cancelText: "Cancel",
        title: _t("Enter Wallet Code"),
        body: "",
        startingValue: "",
    };
    Registries.Component.add(SetCouponCodePopup);
    return SetCouponCodePopup;
});
