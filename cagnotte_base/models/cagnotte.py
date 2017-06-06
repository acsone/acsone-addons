# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _


class CagnotteType(models.Model):
    _name = 'cagnotte.type'
    _description = 'Cagnotte Type'

    name = fields.Char(
        translate=True,
        required=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Cagnotte Sequence',
        help="This field contains the information related to the numbering "
             "of the cagnotte of this type.",
        required=True)
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account', ondelete='restrict',
        index=True,
        required=True)
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal', ondelete='restrict',
        help='Journal use to empty the cagnotte',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product', ondelete='restrict',
        help='Product use to fill the cagnotte')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id,
        required=True)

    @api.constrains('product_id', 'account_id', 'journal_id')
    def _check_account(self):
        """ Check account defined on product is the same than account defined
            on cagnotte
            Check account defined on journal is the same than account defined
            on cagnotte
        """
        check_ok = True
        for cagnotte in self:
            if cagnotte.product_id:
                product_account_id = cagnotte.product_id.\
                    property_account_income_id.id
                if not product_account_id:
                    product_account_id = cagnotte.product_id.categ_id.\
                        property_account_income_categ_id.id
                if not product_account_id or \
                        product_account_id != cagnotte.account_id.id:
                    check_ok = False
                    break
            journal_debit_account_id = cagnotte.journal_id.\
                default_debit_account_id.id
            if journal_debit_account_id != cagnotte.account_id.id:
                check_ok = False
                break
            journal_credit_account_id = cagnotte.journal_id.\
                default_credit_account_id.id
            if journal_credit_account_id != cagnotte.account_id.id:
                check_ok = False
                break
        if not check_ok:
            raise ValidationError(_('Accounts not corresponding between '
                                    'product, journal and cagnotte'))

    _sql_constraints = [(
        'product_cagnotte_uniq',
        'unique(product_id, company_id)',
        'A cagnotte type with the product already exist'
    ), (
        'account_cagnotte_uniq',
        'unique(account_id)',
        'A cagnotte type with this account already exist'
    )]


class AccountCagnotte(models.Model):
    _name = 'account.cagnotte'

    name = fields.Char(
        readonly=True,
        copy=False)
    cagnotte_type_id = fields.Many2one(
        'cagnotte.type',
        'Cagnotte Type',
        required=True,
        ondelete='restrict')
    solde_cagnotte = fields.Float(
        compute='_compute_solde_cagnotte',
        store=True)
    active = fields.Boolean(
        default=True)
    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="account_cagnotte_id",
        string="Journal Items")
    create_date = fields.Date(
        default=fields.Date.today)

    @api.multi
    def _get_name(self):
        self.ensure_one()
        return '%s - %s' % (self.cagnotte_type_id.name, self.name)

    @api.multi
    def name_get(self):
        """Add the type of cagnotte in the name"""
        res = []
        for cagnotte in self:
            name = cagnotte._get_name()
            res.append((cagnotte.id, name))
        return res

    @api.multi
    @api.depends('account_move_line_ids.debit',
                 'account_move_line_ids.credit')
    def _compute_solde_cagnotte(self):
        for cagnotte in self:
            solde_cagnotte = 0
            for move_line in cagnotte.account_move_line_ids:
                solde_cagnotte += move_line.credit - move_line.debit
            cagnotte.solde_cagnotte = solde_cagnotte

    @api.multi
    def create(self, vals):
        if 'name' not in vals:
            cagnotte_type = self.env['cagnotte.type'].browse(
                vals['cagnotte_type_id'])
            vals['name'] = cagnotte_type.sequence_id.next_by_id()
        return super(AccountCagnotte, self).create(vals)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_cagnotte_id = fields.Many2one(
        comodel_name='account.cagnotte',
        string='Cagnotte',
        ondelete='restrict')

    @api.model
    def cagnotte_value(self, values):
        """ If used account is on a cagnotte type,
            create a cagnotte
        """
        if not values.get('account_cagnotte_id'):
            comp = float_compare(values.get('credit', 0.0),
                                 0.0, precision_digits=2)
            if values.get('account_id') and comp != 0:
                cagnotte_type = self.env['cagnotte.type'].search(
                    [('account_id', '=', values['account_id'])])
                if cagnotte_type:
                    # create cagnotte
                    values['account_cagnotte_id'] = \
                        self.env['account.cagnotte'].create(
                            {'cagnotte_type_id': cagnotte_type.id}).id
        return values

    @api.model
    def create(self, values):
        vals = self.cagnotte_value(values)
        return super(AccountMoveLine, self).create(vals)

    @api.constrains('account_cagnotte_id', 'account_id')
    def _check_cagnotte_account(self):
        """ Account must correspond to cagnotte account
        """
        if any(l.account_cagnotte_id and
               l.account_cagnotte_id.cagnotte_type_id.account_id !=
               l.account_id for l in self):
            raise ValidationError(_("The account doesn't correspond"
                                    " to the cagnotte account"))
        return True


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cagnotte_type_id = fields.Many2one(
        comodel_name='cagnotte.type',
        string='Cagnotte type',
        readonly=True,
        ondelete='restrict',
        help="Use this field to give coupon to a customer",
        states={'draft': [('readonly', False)]}
    )

    @api.onchange("cagnotte_type_id")
    def onchange_cagnotte_type_id(self):
        if self.cagnotte_type_id:
            self.account_id = self.cagnotte_type_id.account_id
