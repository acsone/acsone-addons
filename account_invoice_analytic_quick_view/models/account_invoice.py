# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_account_analytic_id(self, invoice_lines):
        ''' compute account_analytic_id by looking at the invoice line,
            and returning the analytic account from the invoice line
            if it is the same on all line. If there are lines with different
            analytic accounts, it must be False.'''
        account = False
        for il in invoice_lines:
            cur_account = False
            if type(il) is dict:
                cur_account = il['account_analytic_id']
            else:
                cur_account = il.account_analytic_id and \
                    il.account_analytic_id.id or False
            if account and account != cur_account:
                return False
            else:
                account = cur_account
        return account

    @api.one
    @api.depends('invoice_line')
    def _account_analytic_id(self):
        self.account_analytic_id = self._get_account_analytic_id(
            self.invoice_line)

    @api.onchange('invoice_line')
    def onchange_invoice_line(self):
        self.account_analytic_id = self._get_account_analytic_id(
            self.invoice_line)

    # new field
    account_analytic_id = fields.Many2one(
        compute='_account_analytic_id',
        comodel_name="account.analytic.account",
        string="Analytic account",
        store=True)
