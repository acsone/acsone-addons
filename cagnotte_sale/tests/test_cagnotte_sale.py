# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.cagnotte_partner.tests.common import CagnotteCommonPartner


class TestCagnotteSale(CagnotteCommonPartner):

    @classmethod
    def setUpClass(cls):
        super(TestCagnotteSale, cls).setUpClass()
        cls.sale = cls.env.ref('sale.sale_order_1')
        cls.product_2 = cls.env.ref('product.product_product_2')
        cls.order_line_obj = cls.env['sale.order.line']

    def _get_line_values(self, discount=False):
        vals = {
            'product_id': self.product_2.id,
            'order_id': self.sale.id,
        }
        line = self.order_line_obj.new(vals)
        line.product_id_change()
        vals = line._convert_to_write(line._cache)
        vals.update({
            'product_uom_qty': 3.0,
            'product_uom': self.product_2.uom_id.id,
        })
        if discount:
            vals.update({
                'price_unit': self.sale.amount_total +
                self.cagnotte.solde_cagnotte + 100.0,
                'product_uom_qty': -1.0,
            })
        return vals

    def _create_order_line(self, discount=False):
        vals = self._get_line_values(discount)
        self.order_line_obj.create(vals)

    def _create_order_line_from_sale(self, discount=False):
        vals = self._get_line_values(discount)
        self.sale.write({
            'order_line': [(0, 0, vals)]
        })

    def test_cagnotte_sale(self):
        # Provision with amount of product + taxes
        self._provision_cagnotte(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEquals(
            -15.00,
            self.cagnotte.sale_order_balance)
        self.sale.unset_cagnotte()
        self.assertEquals(
            len(lines_before),
            len(self.sale.order_line)
        )

    def test_cagnotte_sale_reapply(self):
        self._provision_cagnotte(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self._create_order_line()
        # The new product line is applied + the cagnotte line
        self.assertEquals(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )

    def test_cagnotte_sale_reapply_on_sale_save(self):
        """
        We test a sale order that will apply a line that lead to amount <= 0
        :return:
        """
        self._provision_cagnotte(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self._create_order_line_from_sale(True)
        # We assert that just one line was added (and not 2)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )

    def test_cagnotte_sale_invoiced(self):
        self._provision_cagnotte(15.00)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEquals(
            -15.00,
            self.cagnotte.sale_order_balance)
        self.assertEquals(
            0.00,
            self.cagnotte.solde_cagnotte,
        )
        self.sale.action_confirm()
        for line in self.sale.order_line:
            if line.product_uom_qty != 0:
                line.qty_delivered = line.product_uom_qty
        invoices_id = self.sale.action_invoice_create(final=True)
        self.assertTrue(invoices_id)
        invoice = self.env['account.invoice'].browse(invoices_id[0])
        invoice.action_invoice_open()
        self.cagnotte.invalidate_cache()
        self.assertEquals(
            0.0,
            self.cagnotte.sale_order_balance)
        self.assertEquals(
            0.0,
            self.cagnotte.solde_cagnotte)
