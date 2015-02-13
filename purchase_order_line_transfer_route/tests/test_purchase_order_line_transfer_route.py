# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Adrien Peiffer Nemry Jonathan
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
from datetime import datetime
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from anybox.testing.openerp import SharedSetupTransactionCase


class TestPurchaseOrder(SharedSetupTransactionCase):

    _data_files = ('data/test_purchase_order_line_transfer_route.xml',)

    _module_ns = 'purchase_order_line_transfer_route'

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.project = self.env['project.project']
        self.task = self.env['project.task']
        self.product = self.env['product.product']
        self.partner = self.env['res.partner']
        self.purchase_order = self.env['purchase.order']
        self.purchase_order_line = self.env['purchase.order.line']
        self.stock_location = self.env['stock.location']
        self.stock_warehouse = self.env['stock.warehouse']
        self.stock_loc_route = self.env['stock.location.path']

        self.env['ir.model'].clear_caches()
        self.env['ir.model.data'].clear_caches()

    def test_purchase_order_line_transfer(self):
        route =\
            self.env.ref('%s.stock_location_route_move_it' % self._module_ns)
        partner = self.env.ref('%s.res_partner_supplier' % self._module_ns)
        product = self.env.ref('%s.product_product_cpu' % self._module_ns)
        pricelist = self.env.ref('%s.product_pricelist_qty' % self._module_ns)
        pricelist_id = pricelist.id
        order_qty = 5
        date_planned = datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATE_FORMAT)
        pol_vals = self.registry['purchase.order.line'].onchange_product_id(
            self.env.cr, self.env.uid, [], pricelist_id, product.id, order_qty,
            False, partner_id=False, context=self.env.context)['value']
        pol_vals.update({
            'name': product.name,
            'product_id': product.id,
            'product_qty': order_qty,
            'date_planned': date_planned,
        })
        pol_vals_clone = pol_vals.copy()
        pol_vals_clone['transfer_route_id'] = route.id
        warehouse_ids = self.stock_warehouse.search([('code', '=', 'WH')])
        self.assertTrue(len(warehouse_ids), 'A warehouse should be found')
        po_vals = {
            'partner_id': partner.id,
            'pricelist_id': pricelist_id,
            'payment_term_id': partner.property_supplier_payment_term and
            partner.property_supplier_payment_term.id,
            'location_id': warehouse_ids.lot_stock_id.id,
            'order_line': [[0, False, pol_vals], [0, False, pol_vals_clone]],
        }
        po = self.purchase_order.create(po_vals)
        po.signal_workflow('purchase_confirm')
        self.assertTrue(len(po.picking_ids), 'Should have a picking')
        self.assertTrue(len(po.order_line) == 2, 'Should have a picking')
        theo_natural_location_id =\
            po.picking_type_id.default_location_dest_id.id
        theo_routed_location_id = route.push_ids[0].location_dest_id.id
        theo_location_ids = [theo_routed_location_id, theo_natural_location_id]
        theo_location_ids.sort()
        self.assertEquals(
            len(po.picking_ids.move_lines),  2, 'Should have 2 move lines')
        real_location_ids = []
        for line in po.picking_ids[0].move_lines:
            real_location_ids.append(line.location_dest_id.id)
        real_location_ids.sort()
        self.assertEqual(
            real_location_ids.sort(), theo_location_ids.sort(),
            'Should contains the same ids')
