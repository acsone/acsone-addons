# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    account_wallet_type_id = fields.Many2one(
        comodel_name='account.wallet.type',
        string='Wallet type',
        readonly=True,
        ondelete='restrict',
        help="Use this field to give coupon to a customer",
        states={'draft': [('readonly', False)]},
    )

    @api.onchange("account_wallet_type_id")
    def onchange_account_wallet_type_id(self):
        if self.account_wallet_type_id:
            self.account_id = self.account_wallet_type_id.account_id
