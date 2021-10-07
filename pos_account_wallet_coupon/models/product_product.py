# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    is_wallet_with_coupon = fields.Boolean(
        compute="_compute_is_wallet_with_coupon",
        help="This is a technical field in order to determine if the"
        "product is a Wallet one and force the usage of Coupon.",
    )

    def _get_is_wallet_with_coupon_domain(self):
        return [("with_coupon_code", "=", True), ("product_id", "in", self.ids)]

    def _compute_is_wallet_with_coupon(self):
        WalletTypeObj = self.env["account.wallet.type"]
        wallet_types = WalletTypeObj.search(self._get_is_wallet_with_coupon_domain())
        products = wallet_types.mapped("product_id")
        for product in self:
            product.is_wallet_with_coupon = True if product in products else False
