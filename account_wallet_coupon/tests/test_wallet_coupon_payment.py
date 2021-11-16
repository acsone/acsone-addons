# Copyright 2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form

from .common import WalletCouponCommon


class TestWalletCouponPayment(WalletCouponCommon):
    @classmethod
    def _init_payment_wallet(cls):
        wallet_type = cls.env.ref("account_wallet.wallet_type")
        wallet_type.with_coupon_code = True
        wallet_type.journal_id.payment_credit_account_id = (
            wallet_type.journal_id.default_account_id
        )
        wallet_type.journal_id.payment_debit_account_id = (
            wallet_type.journal_id.default_account_id
        )
        cls.wallet_payment = cls.wallet_obj.create({"wallet_type_id": wallet_type.id})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._init_payment_wallet()

    def test_payment(self):
        """
        Provision wallet with 500.0
        Create an invoice
        Pay with the wallet
        Check the invoice is paid
        Check the wallet balance equals the initial balance - the paid amount
        """
        self._provision_wallet(500.0, wallet=self.wallet_payment)
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as move_form:
            move_form.partner_id = self.partner
            move_form.invoice_date = fields.Date.from_string("2019-01-01")
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_9")
        invoice = move_form.save()
        invoice._post()
        wallet_amount_after = self.wallet_payment.balance - invoice.amount_total
        with Form(
            self.payment_obj.with_context(
                active_ids=invoice.ids, active_model=invoice._name
            )
        ) as payment_form:
            payment_form.journal_id = self.wallet_journal
            payment_form.coupon_code = self.wallet_payment.coupon_id.code

        payment = payment_form.save()
        payment.action_create_payments()

        self.assertEqual("paid", invoice.payment_state)
        self.assertEqual(wallet_amount_after, self.wallet_payment.balance)

    def test_payment_invalid(self):
        """
        Provision wallet with 500.0
        Create an invoice
        Try to pay with an invalid coupon code
        """
        self._provision_wallet(500.0, wallet=self.wallet_payment)
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as move_form:
            move_form.partner_id = self.partner
            move_form.invoice_date = fields.Date.from_string("2019-01-01")
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_9")
        invoice = move_form.save()
        invoice._post()
        with Form(
            self.payment_obj.with_context(
                active_ids=invoice.ids, active_model=invoice._name
            )
        ) as payment_form:
            payment_form.journal_id = self.wallet_journal
            payment_form.coupon_code = "THIS IS AN INVALID ONE"

        payment = payment_form.save()
        with self.assertRaises(UserError):
            payment.action_create_payments()
