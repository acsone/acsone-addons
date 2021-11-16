# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    account_wallet_id = fields.Many2one(
        comodel_name="account.wallet",
    )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """
        Adds the wallet on corresponding payment move line
        """
        res = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals
        )
        if self.account_wallet_id:
            for vals in res:
                if vals["debit"] > 0:
                    vals.update({"account_wallet_id": self.account_wallet_id.id})
        return res
