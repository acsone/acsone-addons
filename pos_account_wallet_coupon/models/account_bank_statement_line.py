# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    account_wallet_id = fields.Many2one(comodel_name="account.wallet", string="Wallet")

    @api.model
    def _prepare_liquidity_move_line_vals(self):
        """
            Transmit the Wallet payment reference to new account move line
        :return: [description]
        :rtype: [type]
        """
        res = super()._prepare_liquidity_move_line_vals()
        if self.account_wallet_id:
            res.update({"account_wallet_id": self.account_wallet_id.id})
        return res
