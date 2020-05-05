# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    def get_price_available(self, order):
        cagnotte_amount = sum(
            order.order_line.filtered('account_cagnotte_id').mapped(
                'price_total'))
        if cagnotte_amount:
            new_order = order.with_context(cagnotte_amount=cagnotte_amount)
        res = super(DeliveryCarrier, self).get_price_available(order=new_order)
        return res
