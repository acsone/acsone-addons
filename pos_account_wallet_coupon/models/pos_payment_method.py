# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    is_wallet_with_coupon = fields.Boolean(
        related="cash_journal_id.is_wallet_with_coupon",
        store=True,
    )

    @api.constrains("is_wallet_with_coupon", "split_transactions")
    def _check_wallet_split_transactions(self):
        for method in self:
            if method.is_wallet_with_coupon and not method.split_transactions:
                raise ValidationError(
                    _(
                        "If the payment method is managed with wallets, "
                        "you should check 'Split Transactions' too."
                    )
                )
