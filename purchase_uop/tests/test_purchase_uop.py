# -*- coding: utf-8 -*-
#
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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
#

import openerp.tests.common as common
from openerp import workflow

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_purchase_uop(common.TransactionCase):

    def setUp(self):
        super(test_purchase_uop, self).setUp()
        self.context = self.registry("res.users").context_get(self.cr,
                                                              self.uid)

    def test_create_purchase_order_invoice_without_uop(self):
        purchase_order_obj = self.registry('purchase.order')
        purchase_order_line_obj = self.registry('purchase.order.line')
        invoice_line_obj = self.registry('account.invoice.line')
        product_id = self.ref('product.product_product_4')
        partner_id = self.ref('base.res_partner_3')
        location_id = self.ref('stock.stock_location_stock')
        order_vals = {'partner_id': partner_id,
                      'location_id': location_id,
                      'invoice_method': 'order',
                      }
        res = purchase_order_obj \
            .onchange_partner_id(self.cr, self.uid, [], partner_id,
                                 context=self.context)
        order_vals.update(res['value'])
        line_vals = {'product_id': product_id,
                     }
        fiscal_position_id = order_vals.get('fiscal_position_id', False)
        pricelist_id = order_vals.get('pricelist_id', False)
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, 0, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=False, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        order_id = purchase_order_obj.create(self.cr, self.uid, order_vals,
                                             context=self.context)
        product_qty = 10
        price_unit = 10
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, product_qty, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=price_unit, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        line_vals.update({'order_id': order_id,
                          })
        purchase_order_line_obj.create(self.cr, self.uid, line_vals,
                                       context=self.context)
        workflow.trg_validate(self.uid, 'purchase.order', order_id,
                              'purchase_confirm', self.cr)
        res = purchase_order_obj.view_invoice(self.cr, self.uid, [order_id],
                                              context=self.context)
        invoice_id = res['res_id']
        invoice_line_id = self.registry('account.invoice.line')\
            .search(self.cr, self.uid, [('invoice_id', '=', invoice_id)],
                    context=self.context)[0]
        invoice_line = invoice_line_obj.browse(self.cr, self.uid,
                                               [invoice_line_id],
                                               context=self.context)[0]
        self.assertAlmostEqual(invoice_line.quantity, 10, 2,
                               "Quantity isn't correct")
        self.assertAlmostEqual(invoice_line.price_unit, 10, 2,
                               "Price unit isn't correct")

    def test_create_purchase_order_invoice_with_uop(self):
        purchase_order_obj = self.registry('purchase.order')
        purchase_order_line_obj = self.registry('purchase.order.line')
        invoice_line_obj = self.registry('account.invoice.line')
        product_obj = self.registry('product.template')
        product_id = self.ref('product.product_product_4')
        partner_id = self.ref('base.res_partner_3')
        location_id = self.ref('stock.stock_location_stock')
        liter_uom_id = self.ref('product.product_uom_litre')
        product_obj.write(self.cr, self.uid, [product_id],
                          {'uop_id': liter_uom_id,
                           'uop_coeff': 1.5,
                           })
        order_vals = {'partner_id': partner_id,
                      'location_id': location_id,
                      'invoice_method': 'order',
                      }
        res = purchase_order_obj \
            .onchange_partner_id(self.cr, self.uid, [], partner_id,
                                 context=self.context)
        order_vals.update(res['value'])
        line_vals = {'product_id': product_id,
                     }
        fiscal_position_id = order_vals.get('fiscal_position_id', False)
        pricelist_id = order_vals.get('pricelist_id', False)
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, 0, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=False, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        order_id = purchase_order_obj.create(self.cr, self.uid, order_vals,
                                             context=self.context)
        product_qty = 10
        price_unit = 10
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, product_qty, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=price_unit, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        line_vals.update({'order_id': order_id,
                          })
        purchase_order_line_obj.create(self.cr, self.uid, line_vals,
                                       context=self.context)
        workflow.trg_validate(self.uid, 'purchase.order', order_id,
                              'purchase_confirm', self.cr)
        res = purchase_order_obj.view_invoice(self.cr, self.uid, [order_id],
                                              context=self.context)
        invoice_id = res['res_id']
        invoice_line_id = self.registry('account.invoice.line')\
            .search(self.cr, self.uid, [('invoice_id', '=', invoice_id)],
                    context=self.context)[0]
        invoice_line = invoice_line_obj.browse(self.cr, self.uid,
                                               [invoice_line_id],
                                               context=self.context)[0]
        self.assertAlmostEqual(invoice_line.quantity, 15, 2,
                               "Quantity isn't correct")
        self.assertAlmostEqual(invoice_line.price_unit, 6.67, 2,
                               "Price unit isn't correct")
        self.assertEqual(invoice_line.uos_id.id, liter_uom_id,
                         "UOS isn't correct")

    def test_create_purchase_order_stock_invoice_without_uop(self):
        purchase_order_obj = self.registry('purchase.order')
        purchase_order_line_obj = self.registry('purchase.order.line')
        invoice_line_obj = self.registry('account.invoice.line')
        picking_obj = self.registry('stock.picking')
        product_id = self.ref('product.product_product_4')
        partner_id = self.ref('base.res_partner_3')
        location_id = self.ref('stock.stock_location_stock')
        order_vals = {'partner_id': partner_id,
                      'location_id': location_id,
                      'invoice_method': 'picking',
                      }
        res = purchase_order_obj \
            .onchange_partner_id(self.cr, self.uid, [], partner_id,
                                 context=self.context)
        order_vals.update(res['value'])
        line_vals = {'product_id': product_id,
                     }
        fiscal_position_id = order_vals.get('fiscal_position_id', False)
        pricelist_id = order_vals.get('pricelist_id', False)
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, 0, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=False, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        order_id = purchase_order_obj.create(self.cr, self.uid, order_vals,
                                             context=self.context)
        product_qty = 10
        price_unit = 10
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, product_qty, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=price_unit, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        line_vals.update({'order_id': order_id,
                          })
        purchase_order_line_obj.create(self.cr, self.uid, line_vals,
                                       context=self.context)
        workflow.trg_validate(self.uid, 'purchase.order', order_id,
                              'purchase_confirm', self.cr)
        res = purchase_order_obj.view_picking(self.cr, self.uid, [order_id],
                                              context=self.context)
        picking_id = res['res_id']
        picking_obj.do_transfer(self.cr, self.uid, [picking_id],
                                context=self.context)
        self.context['active_ids'] = [picking_id]
        confirmation_id = self.registry('stock.invoice.onshipping')\
            .create(self.cr, self.uid, {}, context=self.context)
        invoice_id = self.registry('stock.invoice.onshipping')\
            .create_invoice(self.cr, self.uid, [confirmation_id],
                            context=self.context)[0]
        invoice_line_id = self.registry('account.invoice.line')\
            .search(self.cr, self.uid, [('invoice_id', '=', invoice_id)],
                    context=self.context)[0]
        invoice_line = invoice_line_obj.browse(self.cr, self.uid,
                                               [invoice_line_id],
                                               context=self.context)[0]
        self.assertAlmostEqual(invoice_line.quantity, 10, 2,
                               "Quantity isn't correct")
        self.assertAlmostEqual(invoice_line.price_unit, 10, 2,
                               "Price unit isn't correct")

    def test_create_purchase_order_stock_invoice_with_uop(self):
        purchase_order_obj = self.registry('purchase.order')
        purchase_order_line_obj = self.registry('purchase.order.line')
        invoice_line_obj = self.registry('account.invoice.line')
        product_obj = self.registry('product.template')
        picking_obj = self.registry('stock.picking')
        product_id = self.ref('product.product_product_4')
        partner_id = self.ref('base.res_partner_3')
        location_id = self.ref('stock.stock_location_stock')
        liter_uom_id = self.ref('product.product_uom_litre')
        product_obj.write(self.cr, self.uid, [product_id],
                          {'uop_id': liter_uom_id,
                           'uop_coeff': 1.5,
                           })
        order_vals = {'partner_id': partner_id,
                      'location_id': location_id,
                      'invoice_method': 'picking',
                      }
        res = purchase_order_obj \
            .onchange_partner_id(self.cr, self.uid, [], partner_id,
                                 context=self.context)
        order_vals.update(res['value'])
        line_vals = {'product_id': product_id,
                     }
        fiscal_position_id = order_vals.get('fiscal_position_id', False)
        pricelist_id = order_vals.get('pricelist_id', False)
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, 0, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=False, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        order_id = purchase_order_obj.create(self.cr, self.uid, order_vals,
                                             context=self.context)
        product_qty = 10
        price_unit = 10
        res = purchase_order_line_obj\
            .onchange_product_id(self.cr, self.uid, [], pricelist_id,
                                 product_id, product_qty, False, partner_id,
                                 date_order=False,
                                 fiscal_position_id=fiscal_position_id,
                                 date_planned=False, name=False,
                                 price_unit=price_unit, state='draft',
                                 context=self.context)
        line_vals.update(res['value'])
        line_vals.update({'order_id': order_id,
                          })
        purchase_order_line_obj.create(self.cr, self.uid, line_vals,
                                       context=self.context)
        workflow.trg_validate(self.uid, 'purchase.order', order_id,
                              'purchase_confirm', self.cr)
        res = purchase_order_obj.view_picking(self.cr, self.uid, [order_id],
                                              context=self.context)
        picking_id = res['res_id']
        picking_obj.do_transfer(self.cr, self.uid, [picking_id],
                                context=self.context)
        self.context['active_ids'] = [picking_id]
        confirmation_id = self.registry('stock.invoice.onshipping')\
            .create(self.cr, self.uid, {}, context=self.context)
        invoice_id = self.registry('stock.invoice.onshipping')\
            .create_invoice(self.cr, self.uid, [confirmation_id],
                            context=self.context)[0]
        invoice_line_id = self.registry('account.invoice.line')\
            .search(self.cr, self.uid, [('invoice_id', '=', invoice_id)],
                    context=self.context)[0]
        invoice_line = invoice_line_obj.browse(self.cr, self.uid,
                                               [invoice_line_id],
                                               context=self.context)[0]
        self.assertAlmostEqual(invoice_line.quantity, 15, 2,
                               "Quantity isn't correct")
        self.assertAlmostEqual(invoice_line.price_unit, 6.67, 2,
                               "Price unit isn't correct")
        self.assertEqual(invoice_line.uos_id.id, liter_uom_id,
                         "UOS isn't correct")
