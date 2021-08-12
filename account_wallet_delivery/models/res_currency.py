# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    def _convert(self, from_amount, to_currency, company, date, round=True):
        wallet_amount = self.env.context.get("wallet_amount")
        if wallet_amount:
            # As we want to find back the original amount before the
            # use of cagnotte amounts, we need to add the amount (which is
            # negative)
            from_amount = from_amount - wallet_amount
        return super()._convert(
            from_amount=from_amount, to_currency=to_currency, company=company, date=date, round=round)
