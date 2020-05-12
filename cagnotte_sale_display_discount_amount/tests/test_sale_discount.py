# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.cagnotte_partner.tests.common import CagnotteCommonPartner


class TestCagnotteSale(CagnotteCommonPartner):

    @classmethod
    def setUpClass(cls):
        super(TestCagnotteSale, cls).setUpClass()
        cls.sale = cls.env.ref('sale.sale_order_1')

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
        self.assertEquals(
            15.0,
            self.sale.discount_total,
        )
        self.assertEquals(
            9705.0,
            self.sale.price_total_no_discount
        )
        self.sale.unset_cagnotte()
        self.assertEquals(
            len(lines_before),
            len(self.sale.order_line)
        )
        self.assertEquals(
            0.0,
            self.sale.discount_total,
        )
        self.assertEquals(
            self.sale.amount_total + self.sale.discount_total,
            self.sale.price_total_no_discount
        )
