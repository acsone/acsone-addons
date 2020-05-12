# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
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
