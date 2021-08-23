# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_wallet.tests.common import WalletCommon


class TestWalletCouponProduct(WalletCommon):

    def test_wallet_product(self):
        """ Create wallet
            Check coupon code is empty
            Configure cagnotte type to generate coupon code
            Create cagnotte
            Check coupon code is filled
        """
        wallet_type = self.env.ref("account_wallet.wallet_type_customer")
        wallet_obj = self.env['account.wallet']
        wallet = wallet_obj.create({'wallet_type_id': wallet_type.id})
        wallet_type.with_coupon_code = True
        wallet = wallet_obj.create({'wallet_type_id': wallet_type.id})
        self.assertTrue(wallet.coupon_id.code)
        self.assertTrue(wallet_type.product_id.is_wallet_with_coupon)
