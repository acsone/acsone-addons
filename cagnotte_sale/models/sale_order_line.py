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

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if 'account_cagnotte_id' not in vals:
            res.order_id._reapply_cagnotte()
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'account_cagnotte_id' not in vals:
            self.mapped('order_id')._reapply_cagnotte()
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        """
        To correctly apply the cagnotte name (and not the product one)
        :return:
        """
        res = super(SaleOrderLine, self).product_id_change()
        if self.account_cagnotte_id:
            self.name = self.account_cagnotte_id.name
        return res
