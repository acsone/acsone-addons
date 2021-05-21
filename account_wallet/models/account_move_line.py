# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_wallet_id = fields.Many2one(
        comodel_name='account.wallet',
        string='Wallet',
        ondelete='restrict',
        index=True,
    )

    def _get_computed_account(self):
        if self.account_wallet_id:
            return self.account_wallet_id.wallet_type_id.account_id
        return super()._get_computed_account()

    @api.onchange("account_wallet_id")
    def _onchange_account_wallet_id(self):
        for line in self.filtered("account_wallet_id"):
            line.account_id = line._get_computed_account()

    def wallet_value(self, vals_list):
        """ If used account is on a wallet type,
            create a wallet
        """
        for values in vals_list:
            if not values.get('account_wallet_id'):
                comp = float_compare(values.get('credit', 0.0),
                                    0.0, precision_digits=2)
                if values.get('account_id') and comp != 0:
                    wallet_type = self.env['account.wallet.type'].search(
                        [('account_id', '=', values['account_id'])])
                    if wallet_type:
                        # create wallet
                        values['account_wallet_id'] = \
                            self.env['account.wallet'].create(
                                {'wallet_type_id': wallet_type.id}).id
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self.wallet_value(vals_list)
        return super().create(vals_list)

    @api.constrains('account_wallet_id', 'account_id')
    def _check_wallet_account(self):
        """ Account must correspond to wallet account
        """
        if any(l.account_wallet_id and
               l.account_wallet_id.wallet_type_id.account_id !=
               l.account_id for l in self):
            raise ValidationError(_("The account doesn't correspond"
                                    " to the wallet account"))
        return True
