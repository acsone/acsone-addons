# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleWalletPay(models.TransientModel):

    _name = "sale.wallet.pay"
    _description = "Pay With Wallet"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        required=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        related="sale_order_id.currency_id",
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        readonly=True,
    )
    amount = fields.Monetary()
    account_wallet_id = fields.Many2one(
        "account.wallet",
        required=True,
    )

    def apply(self):
        self.ensure_one()
        self.sale_order_id.apply_wallet(self.account_wallet_id)
        return True
