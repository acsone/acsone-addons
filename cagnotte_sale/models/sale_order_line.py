# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    account_cagnotte_id = fields.Many2one(
        comodel_name='account.cagnotte',
        ondelete='restrict',
        index=True,
    )

    @api.multi
    def write(self, vals):
        """
        We reapply cagnotte if needed. We don't do it in create() as write() is
        called just after
        :param vals:
        :return:
        """
        res = super(SaleOrderLine, self).write(vals)
        res.mapped('order_id')._reapply_cagnotte()
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.account_cagnotte_id:
            self.name = self.account_cagnotte_id.name
        return res
