# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    account_wallet_id = fields.Many2one(
        comodel_name='account.wallet', string="Wallet")
