# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PosOrderLine(models.Model):

    _inherit = "pos.order.line"

    coupon_code = fields.Char()
    account_wallet_id = fields.Many2one(comodel_name="account.wallet", string="Wallet")

    @api.model
    def _get_wallet_create_domain(self, values):
        return [("product_id", "=", values["product_id"])]

    @api.model
    def _get_wallet_values(self, values):
        """
        If a product that is linked to a Wallet Type is sold
        (gift wallet, ...), create a wallet that will be provisioned
        with the amount on pos order line.
        """
        if values.get("product_id") and not values.get("account_wallet_id"):
            wallet_type = self.env["account.wallet.type"].search(
                self._get_wallet_create_domain(values)
            )
            if wallet_type:
                # create wallet
                wallet_vals = {"wallet_type_id": wallet_type.id}
                coupon_code = values.get("coupon_code")
                if coupon_code:
                    coupon = (
                        self.env["coupon.coupon"]
                        .sudo()
                        .create(
                            {
                                "code": coupon_code,
                            }
                        )
                    )
                    wallet_vals.update(
                        {
                            "coupon_id": coupon.id,
                        }
                    )
                values["account_wallet_id"] = (
                    self.env["account.wallet"].create(wallet_vals).id
                )

    @api.model
    def create(self, values):
        self._get_wallet_values(values)
        res = super().create(values)
        return res
