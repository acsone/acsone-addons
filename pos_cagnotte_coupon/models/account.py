# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_cagnotte = fields.Boolean(compute="_compute_has_cagnotte")

    @api.multi
    def _compute_has_cagnotte(self):
        for product in self:
            cagnotte_type_count = self.env['cagnotte.type'].search_count(
                [('product_id', '=', product.id),
                 ('with_coupon_code', '=', True)])
            product.has_cagnotte = cagnotte_type_count > 0


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    has_cagnotte = fields.Boolean(compute="_compute_has_cagnotte")
    check_cagnotte_amount = fields.Boolean(
        compute='_compute_check_cagnotte_amount')

    @api.multi
    def _compute_has_cagnotte(self):
        for journal in self:
            cagnotte_type_count = self.env['cagnotte.type'].search_count(
                [('journal_id', '=', journal.id),
                 ('with_coupon_code', '=', True)])
            journal.has_cagnotte = cagnotte_type_count > 0

    @api.multi
    def _compute_check_cagnotte_amount(self):
        for journal in self:
            cagnotte_type_count = self.env['cagnotte.type'].search_count(
                [('journal_id', '=', journal.id),
                 ('with_coupon_code', '=', True),
                 ('check_cagnotte_amount', '=', True)])
            journal.check_cagnotte_amount = cagnotte_type_count > 0


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    account_cagnotte_id = fields.Many2one('account.cagnotte', 'Cagnotte')


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def _prepare_move_line_vals(
            self, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, partner_id=False):
        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            st_line, move_id, debit, credit, currency_id=currency_id,
            amount_currency=amount_currency, account_id=account_id,
            partner_id=partner_id)
        res['account_cagnotte_id'] = st_line.account_cagnotte_id.id
        return res


class AccountCagnotte(models.Model):
    _inherit = 'account.cagnotte'

    account_bank_statement_line_ids = fields.One2many(
        "account.bank.statement.line", "account_cagnotte_id",
        string="Bank Statement")

    @api.one
    @api.depends('account_bank_statement_line_ids.journal_entry_id',
                 'account_bank_statement_line_ids.amount')
    def _compute_solde_cagnotte(self):
        super(AccountCagnotte, self)._compute_solde_cagnotte()
        solde_cagnotte = self.solde_cagnotte
        # remove amount of statement not done
        for bs_line in self.account_bank_statement_line_ids:
            if not bs_line.journal_entry_id:
                solde_cagnotte -= bs_line.amount
        self.solde_cagnotte = solde_cagnotte


class CagnotteType(models.Model):
    _inherit = 'cagnotte.type'

    check_cagnotte_amount = fields.Boolean()
