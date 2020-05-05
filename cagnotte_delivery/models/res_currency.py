# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    @api.multi
    def compute(self, from_amount, to_currency, round=True):
        cagnotte_amount = self.env.context.get("cagnotte_amount")
        if cagnotte_amount:
            from_amount = from_amount + cagnotte_amount
        return super(ResCurrency, self).compute(
            from_amount=from_amount, to_currency=to_currency, round=round)
