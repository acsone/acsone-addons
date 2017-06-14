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
        for product in self:
            cagnotte_type_count = CagnotteTypeObj.search_count([
                ('product_id', '=', product.id),
                ('with_coupon_code', '=', True)
            ])
            product.has_cagnotte = cagnotte_type_count > 0
