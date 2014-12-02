# -*- coding: utf-8 -*-
#
##############################################################################
#
#     Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv import orm, fields
from openerp.addons import decimal_precision as dp


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid,
                                                            account_id,
                                                            order_line,
                                                            context=context)
        if order_line.product_uop_qty and order_line.product_uop.id:
            uop_coeff = order_line.product_qty and\
                order_line.product_uop_qty / order_line.product_qty or 1.0
            pu = 0.0
            pu = round(order_line.price_unit / uop_coeff,
                       self.pool.get('decimal.precision')
                           .precision_get(cr, uid, 'Product Price'))
            res.update({'price_unit': pu,
                        'quantity': order_line.product_uop_qty,
                        'uos_id': order_line.product_uop.id
                        })
        return res

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
                                 group_id, context=None):
        res = super(purchase_order, self)\
            ._prepare_order_line_move(cr, uid, order, order_line, picking_id,
                                      group_id, context=context)
        if order_line.product_uop_qty and order_line.product_uop.id:
            uop_coeff = order_line.product_qty and\
                order_line.product_uop_qty / order_line.product_qty or 1.0
            for partial_res in res:
                partial_res.update({'product_uos': order_line.product_uop.id,
                                    'product_uos_qty':
                                        partial_res['product_uom_qty'] *
                                        uop_coeff,
                                    })
        return res


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'product_uop_qty': fields.float(string='Quantity (UoP)',
                                        digits_compute=dp.
                                        get_precision('Product UoS'),
                                        readonly=True,
                                        states={'draft':
                                                [('readonly', False)],
                                                'confirmed':
                                                [('readonly', False)]
                                                }
                                        ),
        'product_uop': fields.many2one('product.uom', string='Product UoP'),
    }

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            uop=False, qty_uop=0.0, context=None):
        res = super(purchase_order_line, self)\
            .onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty,
                                 uom_id, partner_id, date_order=date_order,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=date_planned, name=name,
                                 price_unit=price_unit, state=state,
                                 context=context)
        if not product_id:
            return res
        if not res:
            res = {}
        if not res.get('value', False):
            res['value'] = {}
        if not res.get('domain', False):
            res['domain'] = {}
        product_uom_id_obj = self.pool['product.uom']
        product_obj = self.pool['product.product']
        product = product_obj.browse(cr, uid, product_id, context=context)
        if uop:
            if product.uop_id:
                uop2 = product_uom_id_obj.browse(cr, uid, uop)
                if product.uos_id.category_id.id != uop2.category_id.id:
                    uop = False
            else:
                uop = False

        if (not uom_id) and (not uop):
            res['value']['product_uom'] = product.uom_id and\
                product.uom_id.id
            if product.uop_id:
                res['value']['product_uop'] = product.uop_id.id
                res['value']['product_uop_qty'] = qty * product.uop_coeff
                uop_category_id = product.uop_id.category_id.id
            else:
                res['value']['product_uop'] = False
                res['value']['product_uop_qty'] = qty
                uop_category_id = False
            res['domain'].update(
                {'product_uom': [('category_id', '=',
                                  product.uom_id.category_id.id)],
                 'product_uop': [('category_id', '=', uop_category_id)]
                 })
        elif uop and not uom_id:
            res['value']['product_uom'] = product.uom_id and\
                product.uom_id.id
            res['value']['product_uom_qty'] = qty_uop / product.uop_coeff
        elif uom_id:
            if product.uop_id:
                res['value']['product_uop'] = product.uop_id.id
                res['value']['product_uop_qty'] = qty * product.uop_coeff
            else:
                res['value']['product_uop'] = False
                res['value']['product_uop_qty'] = qty
        return res

    onchange_product_id_uop = onchange_product_id

    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty,
                             uom_id, partner_id, date_order=False,
                             fiscal_position_id=False, date_planned=False,
                             name=False, price_unit=False, state='draft',
                             uop=False, qty_uop=0.0, context=None):
        """ Add uop and qty_uop"""
        if context is None:
            context = {}
        if not uom_id:
            return {'value': {'price_unit': price_unit or 0.0, 'name': name
                              or '', 'product_uom': uom_id or False}}
        context = dict(context, purchase_uom_check=True)
        return self.onchange_product_id_uop(cr, uid, ids, pricelist_id, product_id,
                                        qty, uom_id, partner_id,
                                        date_order=date_order,
                                        fiscal_position_id=fiscal_position_id,
                                        date_planned=date_planned, name=name,
                                        price_unit=price_unit, state=state,
                                        uop=uop, qty_uop=qty_uop,
                                        context=context)

    onchange_product_uom_uop = onchange_product_uom
