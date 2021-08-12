# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form
from odoo.addons.account_wallet.tests.common import WalletCommon


class TestCagnotteDelivery(WalletCommon):

    @classmethod
    def setUpClass(cls):
        super(TestCagnotteDelivery, cls).setUpClass()
        cls.sale = cls.env.ref('account_wallet_delivery.sale_order_wallet_delivery')
        cls.product_2 = cls.env.ref('product.product_product_2')
        cls.order_line_obj = cls.env['sale.order.line']
        cls.carrier = cls.env.ref("delivery.delivery_carrier")

        vals = {
            "name": "The Great Carrier",
            "delivery_type": "base_on_rule",
            "product_id": cls.env.ref("delivery.product_product_delivery_poste").id,
            "fixed_price": 20.0,
        }
        cls.carrier = cls.env["delivery.carrier"].create(vals)

        vals = {
            "carrier_id": cls.carrier.id,
            "max_value": 8800,
            "operator": ">=",
            "variable": "price",
            "list_base_price": 10.0,
            "list_price": 0.0,
        }
        cls.env["delivery.price.rule"].create(vals)
        vals = {
            "carrier_id": cls.carrier.id,
            "max_value": 0.0,
            "operator": ">=",
            "variable": "price",
            "list_base_price": 20.0,
            "list_price": 0.0,
        }
        cls.env["delivery.price.rule"].create(vals)

    def test_wallet_sale(self):
        # Sale order total amount = 8850
        # Apply delivery rules
        # As amount is >= 8800, delivery price should be 10.0
        # Pay order with wallet
        # Sale order amount is 8850 - 7.0
        # Apply delivery rules
        # Delivery Price should remain 10.0
        self.sale.write({"carrier_id": self.carrier.id})
        delivery_wizard = Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id': self.sale.id,
            'default_carrier_id': self.carrier.id
        }))
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()
        delivery_line = self.sale.order_line.filtered("is_delivery")
        self.assertTrue(delivery_line)
        self.assertEqual(
            10.0,
            delivery_line.price_total
        )
        self._provision_wallet(7.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -7.00,
            self.wallet.sale_order_balance)

        self.sale.write({"carrier_id": self.carrier.id})
        delivery_wizard = Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id': self.sale.id,
            'default_carrier_id': self.carrier.id
        }))
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        delivery_line = self.sale.order_line.filtered("is_delivery")
        self.assertTrue(delivery_line)
        self.assertEqual(
            10.0,
            delivery_line.price_total
        )

    def test_cagnotte_sale_greater(self):
        # Sale order total amount = 8850
        # Pay order with wallet of 500.0
        # Sale order amount is 8850 - 500.0 = 8350
        # Apply delivery rules
        # Delivery Price should remain 10.0 as wallet payment should not
        # be taken into account
        self._provision_wallet(500.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.assertEqual(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEqual(
            -500.00,
            self.wallet.sale_order_balance)

        self.sale.write({"carrier_id": self.carrier.id})
        delivery_wizard = Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id': self.sale.id,
            'default_carrier_id': self.carrier.id
        }))
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        delivery_line = self.sale.order_line.filtered("is_delivery")
        self.assertTrue(delivery_line)
        self.assertEqual(
            10.0,
            delivery_line.price_total
        )
