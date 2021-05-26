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
        return self.order_line_obj.create(vals)

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
        cagnotte_line = self.sale.order_line.filtered("account_cagnotte_id")
        self.assertEquals(
            cagnotte_line.name,
            self.cagnotte._get_name(),
        )
        self.sale.unset_cagnotte()
        self.assertEquals(
            len(lines_before),
            len(self.sale.order_line)
        )

    def test_cagnotte_sale_reapply_on_line_add(self):
        self._provision_cagnotte(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        line = self._create_order_line()
        # The new product line is applied + the cagnotte line
        self.assertEquals(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )
        line.write({
            "discount": 50,
        })
        self.assertEquals(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )

        self.sale.unlink()
        self.assertEquals(
            15.0,
            self.cagnotte.solde_cagnotte)

    def test_cagnotte_sale_multiple_reapply_on_line_add(self):
        # Provision exsiting cagnotte
        # Create a new one
        #
        self._provision_cagnotte(7.0)
        vals = {
            'cagnotte_type_id': self.cagnotte_type.id,
        }
        self.cagnotte_2 = self.cagnotte_obj.create(vals)
        self._provision_cagnotte(20.0, self.cagnotte_2)

        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.sale.apply_cagnotte(self.cagnotte_2)
        self.assertEquals(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )

        self._create_order_line()
        # The new product line is applied + the txo cagnotte lines
        self.assertEquals(
            len(lines_before) + 3,
            len(self.sale.order_line)
        )
        self.assertEquals(
            2,
            len(self.sale.order_line.filtered('account_cagnotte_id'))
        )

    def test_cagnotte_sale_discount_line(self):
        self.sale.order_line = False
        vals = self._get_line_values()
        vals.update({'price_unit': 5.0})
        line = self.order_line_obj.create(vals)
        self._provision_cagnotte(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        line_cagnotte = self.sale.order_line.filtered('account_cagnotte_id')
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEquals(
            -15.0,
            line_cagnotte.price_total
        )
        self.sale.write({
            'order_line': [(1, line.id, {"discount": 50})]
        })
        line_cagnotte = self.sale.order_line.filtered('account_cagnotte_id')
        self.assertEquals(
            -7.5,
            line_cagnotte.price_total
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
        cagnotte_line = invoice.invoice_line_ids.filtered(
            'account_cagnotte_id')
        self.assertEquals(
            1,
            len(cagnotte_line)
        )
        cagnotte_move_line = invoice.move_id.line_ids.filtered(
            'account_cagnotte_id')
        self.assertEquals(
            1,
            len(cagnotte_move_line)
        )
        self.cagnotte.invalidate_cache()
        self.assertEquals(
            0.0,
            self.cagnotte.sale_order_balance)
        self.assertEquals(
            0.0,
            self.cagnotte.solde_cagnotte)

    def test_cagnotte_sale_cancelled(self):
        self._provision_cagnotte(15.00)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)    
        self.assertEqual(
            1,
            len(self.cagnotte.sale_order_line_not_invoiced_ids)
        )
        self.assertEqual(
            1,
            len(self.cagnotte.sale_order_line_ids)
        )
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
        self.sale.action_cancel()
        self.assertEqual(
            1,
            len(self.cagnotte.sale_order_line_not_invoiced_ids)
        )
        self.assertEqual(
            1,
            len(self.cagnotte.sale_order_line_ids)
        )
        self.assertEquals(
            0.00,
            self.cagnotte.sale_order_balance)
        self.cagnotte._compute_solde_cagnotte()
        self.assertEquals(
            15.00,
            self.cagnotte.solde_cagnotte,
        )
