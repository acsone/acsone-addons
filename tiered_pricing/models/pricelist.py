# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Pigeon Cédric
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api, fields, exceptions
from openerp.tools.translate import _


class product_pricelist(models.Model):
    _inherit = "product.pricelist"

    tiered_pricing = fields.Boolean('Tiered Pricing')

    def _compute_tiered_pricing(self, products_by_qty_by_partner, pricelist,
                                version, rules):
        """
            Recursive method to compute all levels of the tiered pricing
        """
        res = {}
        for product, qty, partner in products_by_qty_by_partner:
            amount = 0.0
            for rule in rules:
                if rule.min_quantity <= qty:
                    prod_by_qty_by_partner = [(product,
                                              qty, partner)]
                    res = super(product_pricelist,
                                self)._price_rule_get_multi(
                        pricelist, prod_by_qty_by_partner,
                        version=version)
                    unit_price = res[product.id][0] or 0.00
                    level_qty = (qty - rule.min_quantity) + 1
                    amount += unit_price * level_qty
                    remain = qty - level_qty
                    if remain == 0:
                        break
                    else:
                        prod_by_qty_by_partner = [(product,
                                                  remain, partner)]
                        res = self._compute_tiered_pricing(
                            prod_by_qty_by_partner, pricelist,
                            version, rules)
                        amount += res[product.id]
                        break
            res[product.id] = amount
        return res

    @api.model
    def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner,
                              version=False):
        if pricelist.tiered_pricing:
            product_uom_obj = self.pool.get('product.uom')
            version = self._get_pricelist_current_version(pricelist)
            products = map(lambda x: x[0], products_by_qty_by_partner)

            is_product_template = products[0]._name == "product.template"
            rules = self._get_pricelist_rules(products, is_product_template,
                                              version)
            results = {}
            for product, qty, partner in products_by_qty_by_partner:
                qty_uom_id = self._context.get('uom') or product.uom_id.id
                qty_in_product_uom = qty
                if qty_uom_id != product.uom_id.id:
                    try:
                        qty_in_product_uom = product_uom_obj._compute_qty(
                            qty_uom_id, qty, product.uom_id.id
                            or product.uos_id.id)
                    except exceptions.except_orm:
                        pass
                prod_by_qty_by_partner = [(product, qty_in_product_uom,
                                           partner)]
                amount = self._compute_tiered_pricing(prod_by_qty_by_partner,
                                                      pricelist,
                                                      version, rules)
                results[product.id] = (amount[product.id] / qty, False)
            return results
        else:
            return super(product_pricelist, self)._price_rule_get_multi(
                pricelist, products_by_qty_by_partner, version=version)


class product_pricelist_version(models.Model):
    _inherit = "product.pricelist.version"

    @api.constrains('items_id')
    def _check_rules_consistency(self):
        self.items_id._check_quantity_consistency()


class product_pricelist_item(models.Model):
    _inherit = "product.pricelist.item"

    @api.one
    @api.depends('price_version_id')
    def _get_tiered_pricing(self):
        self.tiered_pricing = self.price_version_id.pricelist_id.tiered_pricing

    tiered_pricing = fields.Boolean('Tiered Pricing',
                                    compute=lambda self:
                                    self._get_tiered_pricing())

    @api.one
    @api.constrains('min_quantity')
    def _check_quantity_consistency(self):
        if self.tiered_pricing:
            if self.min_quantity == 0:
                raise exceptions.Warning(
                    _('Minimum Quantity O is not allowed'
                      ' for tiered pricing !'))
            min_ceilings = []
            for item in self.price_version_id.items_id:
                if item.min_quantity not in min_ceilings:
                    min_ceilings.append(item.min_quantity)
                else:
                    raise exceptions.Warning(
                        _('Minimum Quantity must be unique in pricelist'
                          ' version for tiered pricing: %s appears several'
                          ' times !' % item.min_quantity))
            if 1 not in min_ceilings:
                raise exceptions.Warning(
                    _('The first rule of a tiered pricing must have'
                      ' a minimum quantity of 1 unit !'))

    @api.model
    def create(self, vals):
        vals['sequence'] = 0
        return super(product_pricelist_item, self).create(vals)
