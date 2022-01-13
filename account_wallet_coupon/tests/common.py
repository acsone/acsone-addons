# Copyright 2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_wallet.tests.common import WalletCommon


class WalletCouponCommon(WalletCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["account.move"]
        cls.payment_obj = cls.env["account.payment.register"]
