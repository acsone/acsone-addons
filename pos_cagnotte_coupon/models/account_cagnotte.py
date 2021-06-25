# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountCagnotte(models.Model):
    _inherit = 'account.cagnotte'

    account_bank_statement_line_ids = fields.One2many(
        comodel_name='account.bank.statement.line',
        inverse_name='account_cagnotte_id',
        string="Bank Statement")

    @api.multi
    @api.depends(
        'account_bank_statement_line_ids.journal_entry_ids',
        'account_bank_statement_line_ids.amount')
    def _compute_solde_cagnotte(self):
        super(AccountCagnotte, self)._compute_solde_cagnotte()
        for rec in self:
            solde_cagnotte = rec.solde_cagnotte
            # remove amount of statement not done
            for bs_line in rec.account_bank_statement_line_ids:
                if not bs_line.journal_entry_ids:
                    solde_cagnotte -= bs_line.amount
            rec.solde_cagnotte = solde_cagnotte
