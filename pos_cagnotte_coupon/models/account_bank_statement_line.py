# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    account_cagnotte_id = fields.Many2one(
        comodel_name='account.cagnotte', string="Cagnotte")

    @api.multi
    def _prepare_reconciliation_move_line(self, move, amount):
        self.ensure_one()
        values = super(AccountBankStatementLine, self).\
            _prepare_reconciliation_move_line(move, amount)
        account_cagnotte = self.account_cagnotte_id
        if account_cagnotte:
            values['account_cagnotte_id'] = account_cagnotte.id
        return values
