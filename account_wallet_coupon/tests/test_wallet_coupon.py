# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form

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

    def test_payment(self):
        """
        Provision wallet with 500.0
        Create an invoice
        Pay with the wallet
        Check the invoice is paid
        Check the wallet balance equals the initial balance - the paid amount
        """
        wallet_type = self.env.ref("account_wallet.wallet_type")
        wallet_type.with_coupon_code = True
        wallet_type.journal_id.payment_credit_account_id = (
            wallet_type.journal_id.default_account_id
        )
        wallet_type.journal_id.payment_debit_account_id = (
            wallet_type.journal_id.default_account_id
        )
        wallet = self.wallet_obj.create({"wallet_type_id": wallet_type.id})
        self._provision_wallet(500.0, wallet=wallet)
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as move_form:
            move_form.partner_id = self.partner
            move_form.invoice_date = fields.Date.from_string("2019-01-01")
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_9")
        invoice = move_form.save()
        invoice._post()
        wallet_amount_after = wallet.balance - invoice.amount_total
        with Form(
            self.payment_obj.with_context(
                active_ids=invoice.ids, active_model=invoice._name
            )
        ) as payment_form:
            payment_form.journal_id = self.wallet_journal
            payment_form.coupon_code = wallet.coupon_id.code

        payment = payment_form.save()
        payment.action_create_payments()

        self.assertEqual("paid", invoice.payment_state)
        self.assertEqual(wallet_amount_after, wallet.balance)
