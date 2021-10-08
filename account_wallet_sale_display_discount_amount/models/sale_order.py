# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_compute_discount_total_depends(self):
        res = super()._get_compute_discount_total_depends()
        res.append("order_line.account_wallet_id")
        return res

    @api.depends(lambda self: self._get_compute_discount_total_depends())
    def _compute_discount_total(self):
        """
        We just influence the total without discount
        :return:
        """
        super()._compute_discount_total()
        for order in self:
            price_total_no_discount = order.price_total_no_discount
            for line in order.order_line.filtered("account_wallet_id"):
                price_total = line.price_total
                if (
                    float_compare(
                        line.price_total,
                        0.0,
                        precision_rounding=line.currency_id.rounding,
                    )
                    < 1
                ):
                    price_total = -price_total
                price_total_no_discount += price_total
            # If order is NewId, currency_id is maybe not filled yet
            if order.currency_id and (
                float_compare(
                    price_total_no_discount,
                    order.price_total_no_discount,
                    precision_rounding=order.currency_id.rounding,
                )
                != 0
            ):
                order.update(
                    {
                        "price_total_no_discount": price_total_no_discount,
                    }
                )
