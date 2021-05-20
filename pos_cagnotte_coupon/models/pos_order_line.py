# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PosOrderLine(models.Model):

    _inherit = 'pos.order.line'

    coupon_code = fields.Char()
    account_cagnotte_id = fields.Many2one(
        comodel_name='account.cagnotte', string="Cagnotte")

    @api.model
    def create(self, values):
        if values.get('product_id') and not values.get('account_cagnotte_id'):
            cagnotte_type = self.env['cagnotte.type'].search(
                [('product_id', '=', values['product_id'])])
            if cagnotte_type:
                # create cagnotte
                cagnotte_vals = {'cagnotte_type_id': cagnotte_type.id}
                if values.get('coupon_code'):
                    cagnotte_vals['coupon_code'] = values['coupon_code']
                values['account_cagnotte_id'] = \
                    self.env['account.cagnotte'].create(cagnotte_vals).id
        res = super(PosOrderLine, self).create(values)
        return res
