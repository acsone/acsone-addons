# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountWalletType(models.Model):
    _name = 'account.wallet.type'
    _description = 'Wallet Type'
    _check_company_auto = True

    name = fields.Char(
        translate=True,
        required=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Wallet Sequence',
        copy=False,
        check_company=True,
        help="This field contains the information related to the numbering "
             "of the wallet of this type.",
        required=True)
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account', ondelete='restrict',
        index=True,
        required=True)
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal', ondelete='restrict',
        help='Journal use to empty the wallet',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product', ondelete='restrict',
        help='Product use to fill the wallet')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True)

    # TODO: Check if this is necessary and if model cannot be simplified
    # @api.constrains('product_id', 'account_id', 'journal_id')
    # def _check_account(self):
    #     """ Check account defined on product is the same than account defined
    #         on wallet
    #         Check account defined on journal is the same than account defined
    #         on wallet
    #     """
    #     check_ok = True
    #     for wallet in self:
    #         if wallet.product_id:
    #             product_account_id = wallet.product_id.\
    #                 property_account_income_id.id
    #             if not product_account_id:
    #                 product_account_id = wallet.product_id.categ_id.\
    #                     property_account_income_categ_id.id
    #             if not product_account_id or \
    #                     product_account_id != wallet.account_id.id:
    #                 check_ok = False
    #                 break
    #         journal_loss_account_id = wallet.journal_id.\
    #             loss_account_id.id
    #         if journal_loss_account_id != wallet.account_id.id:
    #             check_ok = False
    #             break
    #         journal_profit_account_id = wallet.journal_id.\
    #             profit_account_id.id
    #         if journal_profit_account_id != wallet.account_id.id:
    #             check_ok = False
    #             break
    #     if not check_ok:
    #         raise ValidationError(_('Accounts not corresponding between '
    #                                 'product, journal and cagnotte'))

    _sql_constraints = [(
        'product_wallet_type_uniq',
        'unique(product_id, company_id)',
        'A wallet type with the product already exists'
    ), (
        'account_wallet_uniq',
        'unique(account_id)',
        'A wallet type with this account already exists'
    )]
