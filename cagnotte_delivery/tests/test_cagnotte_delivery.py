# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.cagnotte_partner.tests.common import CagnotteCommonPartner


class TestCagnotteDelivery(CagnotteCommonPartner):

    @classmethod
    def setUpClass(cls):
        super(TestCagnotteDelivery, cls).setUpClass()
        cls.sale = cls.env.ref('sale.sale_order_1')
        cls.product_2 = cls.env.ref('product.product_product_2')
        cls.order_line_obj = cls.env['sale.order.line']
        cls.carrier = cls.env.ref("delivery.delivery_carrier")

        vals = {
            "name": "The Great Carrier",
            "delivery_type": "base_on_rule",
            "product_type": "service",
            "product_sale_ok": False,
            "fixed_price": 20.0,
        }
        cls.carrier = cls.env["delivery.carrier"].create(vals)

        vals = {
            "carrier_id": cls.carrier.id,
            "max_value": 9685,
            "operator": ">=",
            "variable": "price",
            "list_base_price": 0.0,
            "standard_price": 0.0,
        }
        cls.env["delivery.price.rule"].create(vals)

    def test_cagnotte_sale(self):
        # Provision with amount of product + taxes
        self._provision_cagnotte(7.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEquals(
            -7.00,
            self.cagnotte.sale_order_balance)

        self.sale.write({"carrier_id": self.carrier.id})

        delivery_line = self.sale.order_line.filtered("is_delivery")
        self.assertEquals(
            0.0,
            delivery_line.price_total
        )

    def test_cagnotte_sale_greater(self):
        # Provision with amount
        # Ensure that the rule is applied
        self._provision_cagnotte(500.0)
        lines_before = self.sale.order_line
        self.sale.apply_cagnotte(self.cagnotte)
        self.assertEquals(
            len(lines_before) + 1,
            len(self.sale.order_line)
        )
        self.assertEquals(
            -500.00,
            self.cagnotte.sale_order_balance)

        self.sale.write({"carrier_id": self.carrier.id})

        delivery_line = self.sale.order_line.filtered("is_delivery")
        self.assertEquals(
            0.0,
            delivery_line.price_total
        )
