# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_wallet.tests.common import WalletCommon
from odoo.fields import first


class TestCagnotteSale(WalletCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                self.wallet.balance + 100.0,
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

    def test_wallet_sale(self):
        # Provision with amount of product + taxes
        self._provision_wallet(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -15.00,
            self.wallet.sale_order_balance)
        wallet_line = self.sale.order_line.filtered("account_wallet_id")
        self.assertEqual(
            wallet_line.name,
            self.wallet._get_name(),
        )
        self.sale.unset_wallet()
        self.assertEqual(
            len(lines_before),
            len(self.sale.order_line)
        )

    def test_wallet_sale_reapply_on_line_add(self):
        self._provision_wallet(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        line = self._create_order_line()
        # The new product line is applied + the wallet line
        self.assertEqual(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )
        line.write({
            "discount": 50,
        })
        self.assertEqual(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )

        self.sale.unlink()
        self.assertEqual(
            15.0,
            self.wallet.balance)

    def test_wallet_sale_multiple_reapply_on_line_add(self):
        # Provision exsiting wallet
        # Create a new one
        #
        self._provision_wallet(7.0)
        vals = {
            'wallet_type_id': self.wallet_type.id,
        }
        self.wallet_2 = self.wallet_obj.create(vals)
        self._provision_wallet(20.0, self.wallet_2)

        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.sale.apply_wallet(self.wallet_2)
        self.assertEqual(
            len(lines_before) + 2,
            len(self.sale.order_line)
        )

        self._create_order_line()
        # The new product line is applied + the two wallet lines
        self.assertEqual(
            len(lines_before) + 3,
            len(self.sale.order_line)
        )
        self.assertEqual(
            2,
            len(self.sale.order_line.filtered('account_wallet_id'))
        )

    def test_wallet_sale_discount_line(self):
        self.sale.order_line = False
        vals = self._get_line_values()
        vals.update({'price_unit': 5.0})
        line = self.order_line_obj.create(vals)
        self._provision_wallet(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        line_wallet = self.sale.order_line.filtered('account_wallet_id')
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -15.0,
            line_wallet.price_total
        )
        self.sale.write({
            'order_line': [(1, line.id, {"discount": 50})]
        })
        line_wallet = self.sale.order_line.filtered('account_wallet_id')
        self.assertEqual(
            -7.5,
            line_wallet.price_total
        )

    def test_wallet_sale_reapply_on_sale_save(self):
        """
        We test a sale order that will apply a line that lead to amount <= 0
        :return:
        """
        self._provision_wallet(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self._create_order_line_from_sale(True)
        # We assert that just one line was added (and not 2)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )

    def test_wallet_sale_invoiced(self):
        self._provision_wallet(15.00)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -15.00,
            self.wallet.sale_order_balance)
        self.assertEqual(
            0.00,
            self.wallet.balance,
        )
        self.sale.action_confirm()
        for line in self.sale.order_line:
            if line.product_uom_qty != 0:
                line.qty_delivered = line.product_uom_qty
        invoices = self.sale._create_invoices(final=True)
        self.assertTrue(invoices)
        invoice = first(invoices)
        invoice.action_post()
        wallet_line = invoice.invoice_line_ids.filtered(
            'account_wallet_id')
        self.assertEqual(
            1,
            len(wallet_line)
        )
        wallet_move_line = invoice.invoice_line_ids.filtered(
            'account_wallet_id')
        self.assertEqual(
            1,
            len(wallet_move_line)
        )
        self.wallet.invalidate_cache()
        self.assertEqual(
            0.0,
            self.wallet.sale_order_balance)
        self.assertEqual(
            0.0,
            self.wallet.balance)

    def test_wallet_sale_cancelled(self):
        self._provision_wallet(15.00)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            1,
            len(self.wallet.sale_order_line_not_invoiced_ids)
        )
        self.assertEqual(
            1,
            len(self.wallet.sale_order_line_ids)
        )
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -15.00,
            self.wallet.sale_order_balance)
        self.assertEqual(
            0.00,
            self.wallet.balance,
        )
        self.sale.action_cancel()
        self.assertEqual(
            1,
            len(self.wallet.sale_order_line_not_invoiced_ids)
        )
        self.assertEqual(
            1,
            len(self.wallet.sale_order_line_ids)
        )
        self.assertEqual(
            0.00,
            self.wallet.sale_order_balance)
        self.wallet._compute_balance()
        self.assertEqual(
            15.00,
            self.wallet.balance,
        )
