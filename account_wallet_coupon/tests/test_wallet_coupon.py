# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import WalletCouponCommon


class TestWalletCoupon(WalletCouponCommon):
    def test_wallet(self):
        """Create wallet
        Check coupon code is empty
        Configure cagnotte type to generate coupon code
        Create cagnotte
        Check coupon code is filled
        """
        wallet_type = self.env.ref("account_wallet.wallet_type")
        wallet_obj = self.env["account.wallet"]
        wallet = wallet_obj.create({"wallet_type_id": wallet_type.id})
        self.assertFalse(wallet.coupon_id)
        wallet_type.with_coupon_code = True
        wallet = wallet_obj.create({"wallet_type_id": wallet_type.id})
        self.assertTrue(wallet.coupon_id.code)
