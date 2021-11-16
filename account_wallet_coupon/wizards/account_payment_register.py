# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):

    _inherit = "account.payment.register"

    is_with_coupon = fields.Boolean(
        compute="_compute_is_with_coupon",
    )
    coupon_code = fields.Char()

    def _get_wallet_type_coupon_domain(self):
        return [
            ("journal_id", "in", self.mapped("journal_id").ids),
            ("with_coupon_code", "=", True),
        ]

    @api.depends("journal_id")
    def _compute_is_with_coupon(self):
        wallet_types = self.env["account.wallet.type"].search(
            self._get_wallet_type_coupon_domain()
        )
        for register in self:
            if register.journal_id.id in wallet_types.mapped("journal_id").ids:
                register.is_with_coupon = True
            else:
                register.is_with_coupon = False

    def _get_wallet_from_coupon(self):
        return self.env["account.wallet"].search(
            [("coupon_id.code", "=", self.coupon_code)]
        )

    def _create_payment_vals_from_wizard(self):
        res = super()._create_payment_vals_from_wizard()
        if self.coupon_code:
            wallet = self._get_wallet_from_coupon()
            if wallet:
                res.update({"account_wallet_id": wallet.id})
        return res
