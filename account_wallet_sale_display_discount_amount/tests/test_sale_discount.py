# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_wallet.tests.common import WalletCommon


class TestWalletDisplayAmount(WalletCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale.sale_order_1")

    def test_wallet_sale(self):
        # Provision with amount of product + taxes
        self._provision_wallet(15.0)
        lines_before = self.sale.order_line
        self.sale.apply_wallet(self.wallet)
        self.sale.invalidate_cache()
        self.assertEqual(len(lines_before) + 1, len(self.sale.order_line))
        self.assertEqual(-15.00, self.wallet.sale_order_balance)
        wallet_line = self.sale.order_line.filtered("account_wallet_id")
        self.assertEqual(
            wallet_line.name,
            self.wallet._get_name(),
        )
        self.assertEqual(
            0.0,
            self.sale.discount_total,
        )
        self.assertEqual(9705.0, self.sale.price_total_no_discount)
        self.assertEqual(9690.0, self.sale.amount_total)
        self.sale.unset_wallet()
        self.assertEqual(len(lines_before), len(self.sale.order_line))
        self.assertEqual(
            0.0,
            self.sale.discount_total,
        )
        self.assertEqual(
            self.sale.amount_total + self.sale.discount_total,
            self.sale.price_total_no_discount,
        )
