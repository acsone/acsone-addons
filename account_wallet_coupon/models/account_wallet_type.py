# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountWalletType(models.Model):
    _inherit = "account.wallet.type"

    with_coupon_code = fields.Boolean(
        help="Use this check to generate coupon number on created wallet "
        "for this type"
    )
