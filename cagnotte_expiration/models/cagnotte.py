# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from openerp import api, fields, models


class CagnotteType(models.Model):
    _inherit = 'cagnotte.type'

    expiration_journal_id = fields.Many2one(comodel_name='account.journal',
                                            string='Expiration Journal',
                                            ondelete='restrict')
    expiration_account_id = fields.Many2one(comodel_name='account.account',
                                            string='Expiration Account',
                                            ondelete='restrict')
    expiration_time = fields.Integer(
        default=-1,
        help="Time of expiration (in day) to automatically set the "
             "expiration date on created cagnotte. Set to 0 or less to "
             "ignore expiration")

    @api.multi
    def _check_expiration(self):
        """ If expiration configuration is removed, check no cagnotte needs it
        """
        for cagnotte_type in self:
            if not cagnotte_type.expiration_journal_id or \
                    not cagnotte_type.expiration_account_id:
                if self.env['account.cagnotte'].search_count(
                    [('expiration_date', '!=', False),
                     ('cagnotte_type_id', '=', cagnotte_type.id)]):
                    return False
        return True

    _constraints = [
        (_check_expiration,
         'Expiration cannot be removed, some cagnotte use it',
         ['expiration_journal_id', 'expiration_account_id']),
    ]


class AccountCagnotte(models.Model):
    _inherit = 'account.cagnotte'

    expiration_time = fields.Integer(
        related="cagnotte_type_id.expiration_time")
    expiration_date = fields.Date()

    @api.multi
    @api.onchange("expiration_time")
    def onchange_expiration_time(self):
        """ compute the expiration date
        """
        for cagnotte in self:
            if cagnotte.expiration_time > 0:
                cagnotte.expiration_date = self.compute_expiration_date(
                    cagnotte.expiration_time)
            else:
                cagnotte.expiration_date = False

    @api.model
    def compute_expiration_date(self, expiration_time):
        date_today = fields.Date.from_string(fields.Date.today())
        return date_today + timedelta(days=expiration_time)

    @api.model
    def expiration_date_values(self, values):
        """ Check if expiration_date should be computed
        """
        if values.get('expiration_date'):
            return values
        if not values.get('cagnotte_type_id'):
            return values
        cagnotte_type = self.env['cagnotte.type'].browse(
            values['cagnotte_type_id'])
        if cagnotte_type.expiration_time > 0:
            expiration_date = self.compute_expiration_date(
                cagnotte_type.expiration_time)
            values['expiration_date'] = expiration_date
        return values

    @api.model
    def create(self, vals):
        return super(AccountCagnotte, self).create(
            self.expiration_date_values(vals))

    @api.multi
    def write(self, vals):
        return super(AccountCagnotte, self).write(
            self.expiration_date_values(vals))

    @api.multi
    def _check_expiration(self):
        """ If expiration_date is specificied, check cagnotte type has
            configuration for expiration
        """
        for cagnotte in self:
            if cagnotte.expiration_date:
                if not cagnotte.cagnotte_type_id.expiration_account_id:
                    return False
                if not cagnotte.cagnotte_type_id.expiration_journal_id:
                    return False
        return True

    _constraints = [
        (_check_expiration,
         'Cagnotte type has no expiration configuration',
         ['expiration_date', 'cagnotte_type_id']),
    ]

    @api.one
    def _empty_cagnotte(self):
        move_obj = self.env['account.move']
        amount = self.solde_cagnotte
        if amount:
            date = fields.Date.today()
            period_ids = self.env['account.period'].find(date)
            lines = [(0, 0, {'name': "%s expiration" % self.name_get(),
                             'date': date,
                             'debit': amount < 0 and -amount,
                             'credit': amount > 0 and amount,
                             'account_id':
                             self.cagnotte_type_id.expiration_account_id.id,
                             'quantity': 1.00}),
                     (0, 0, {'name': "%s expiration" % self.name_get(),
                             'date': date,
                             'debit': amount > 0 and amount,
                             'credit': amount < 0 and -amount,
                             'account_id': self.cagnotte_type_id.account_id.id,
                             'account_cagnotte_id': self.id,
                             'quantity': 1.00})]
            move = move_obj.create(
                {'line_id': lines,
                 'journal_id': self.cagnotte_type_id.expiration_journal_id.id,
                 'period_id': period_ids[0].id,
                 'date': date})
            move.validate()

    @api.multi
    def _run_expiration_cagnotte(self):
        """ At the expiration date, empty the cagnotte and set it inactive
        """
        expired_cagnotte = self.search(
            [('expiration_date', '<', fields.Date.today())])
        expired_cagnotte._empty_cagnotte()
        expired_cagnotte.write({'active': False})
        return True
