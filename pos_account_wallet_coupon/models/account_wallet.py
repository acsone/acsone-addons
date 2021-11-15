# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountCagnotte(models.Model):
    _inherit = "account.wallet"

    pos_payment_ids = fields.One2many(
        comodel_name="pos.payment",
        inverse_name="account_wallet_id",
        string="Pos Payment",
    )

    @api.model
    def _get_compute_balance_fields(self):
        """
        As bank statement are not linked to pos payment directly,
        we depends on session state as if it is 'closed', bank
        statements are generated (and moves too).
        """
        fields = [
            "pos_payment_ids",
            "pos_payment_ids.account_wallet_id",
            "pos_payment_ids.amount",
            "pos_payment_ids.session_id.state",
        ]
        res = super()._get_compute_balance_fields()
        for field in fields:
            if field not in res:
                res.append(field)
        return res

    def _compute_balance(self):
        super()._compute_balance()
        for rec in self.filtered(lambda self: self.pos_payment_ids):
            for payment in self.pos_payment_ids.filtered(
                lambda self: self.account_wallet_id
                and self.session_id.state not in ("closing_control", "closed")
            ):
                rec.balance -= payment.amount
