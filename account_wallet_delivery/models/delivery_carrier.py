# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    def _get_price_available(self, order):
        wallet_amount = sum(
            order.order_line.filtered('account_wallet_id').mapped(
                'price_total'))
        new_order = order
        if wallet_amount:
            new_order = order.with_context(wallet_amount=wallet_amount)
        res = super()._get_price_available(order=new_order)
        return res

    def _get_price_dict(self, total, weight, volume, quantity):
        res = super()._get_price_dict(total, weight, volume, quantity)
        return res
