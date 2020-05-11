# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    has_cagnotte = fields.Boolean(compute='_compute_has_cagnotte')

    @api.multi
    def _compute_has_cagnotte(self):
        CagnotteTypeObj = self.env['cagnotte.type']
        cagnotte_type = CagnotteTypeObj.search([
                ('with_coupon_code', '=', True)
        ])
        product_ids = cagnotte_type.mapped('product_id.id')
        for product in self:
            product.has_cagnotte = product.id in product_ids