# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import PosWalletCommon


class TestPointOfSale(PosWalletCommon):

    def test_order_to_invoice(self):
        # Provision a Wallet with 50.0 (the balance is 50.0)
        # Create a POS order
        # Pay with Wallet (the Wallet balance is 0.0)
        # Pay the balance with Cash
        # Close the POS session
        # The Wallet balance is still 0.0

        self._provision_wallet(50.0)

        self.pos_config.open_session_cb(check_coa=False)
        current_session = self.pos_config.current_session_id

        untax1, atax1 = self.compute_tax(self.product3, 450*0.95, 2)
        untax2, atax2 = self.compute_tax(self.product4, 300*0.95, 3)
        # I create a new PoS order with 2 units of PC1 at 450 EUR (Tax Incl) and 3 units of PCSC349 at 300 EUR. (Tax Excl)
        self.pos_order_pos1 = self.PosOrder.create({
            'company_id': self.env.company.id,
            'session_id': current_session.id,
            'partner_id': self.partner1.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 5.0,
                'qty': 2.0,
                'tax_ids': [(6, 0, self.product3.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id).ids)],
                'price_subtotal': untax1,
                'price_subtotal_incl': untax1 + atax1,
            }), (0, 0, {
                'name': "OL/0002",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 5.0,
                'qty': 3.0,
                'tax_ids': [(6, 0, self.product4.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id).ids)],
                'price_subtotal': untax2,
                'price_subtotal_incl': untax2 + atax2,
            })],
            'amount_tax': atax1 + atax2,
            'amount_total': untax1 + untax2 + atax1 + atax2,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })
        payments_before = self.pos_order_pos1.payment_ids
        self.assertEqual(
            50.0,
            self.wallet.balance,
        )
        # I click on the "Make Payment" wizard to pay the PoS order
        context_make_payment = {"active_ids": [self.pos_order_pos1.id], "active_id": self.pos_order_pos1.id}
        self.pos_make_payment = self.PosMakePayment.with_context(context_make_payment).create({
            'amount': 50.0,
            "payment_method_id": self.wallet_payment_method.id,
        })
        # I click on the validate button to register the payment.
        context_payment = {'active_id': self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()
        payments_after = self.pos_order_pos1.payment_ids - payments_before
        self.assertEqual(
            self.wallet_payment_method,
            payments_after.payment_method_id
        )
        payments_after.account_wallet_id = self.wallet
        self.assertEqual(
            0.0,
            self.wallet.balance,
        )

        context_make_payment = {"active_ids": [self.pos_order_pos1.id], "active_id": self.pos_order_pos1.id}
        self.pos_make_payment = self.PosMakePayment.with_context(context_make_payment).create({
            'amount': self.pos_order_pos1.amount_total - 50.0
        })
        # I click on the validate button to register the payment.
        context_payment = {'active_id': self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()

        # I check that the order is marked as paid and there is no invoice
        # attached to it
        self.assertEqual(self.pos_order_pos1.state, 'paid', "Order should be in paid state.")
        self.assertFalse(self.pos_order_pos1.account_move, 'Invoice should not be attached to order.')

        # I close the session to generate the journal entries
        current_session.action_pos_session_closing_control()

        self.assertEqual(
            0.0,
            self.wallet.balance,
        )

    def test_gift_product(self):
        # Create a POS order
        # Sell a Wallet product and set an amount
        # Check if Wallet is created and the amount correctly set after closing
        self._create_gift_wallet_type()
        gift_wallet_before = self.env["account.wallet"].search([("wallet_type_id", "=", self.gift_wallet_type.id)])
        self.assertEqual(
            0,
            len(gift_wallet_before),
        )
        self.pos_config.open_session_cb(check_coa=False)
        current_session = self.pos_config.current_session_id

        untax1, atax1 = self.compute_tax(self.gift_product, 450, 1)
        # I create a new PoS order with 2 units of PC1 at 450 EUR (Tax Incl) and 3 units of PCSC349 at 300 EUR. (Tax Excl)
        self.pos_order_pos1 = self.PosOrder.create({
            'company_id': self.env.company.id,
            'session_id': current_session.id,
            'partner_id': self.partner1.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.gift_product.id,  # Set Gift Product
                'price_unit': 450,  # Provision Gift Wallet
                'qty': 1.0,
                'tax_ids': [(6, 0, self.gift_product.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id).ids)],
                'price_subtotal': untax1,
                'price_subtotal_incl': untax1 + atax1,
            })],
            'amount_tax': atax1,
            'amount_total': untax1 + atax1,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })
        # I click on the validate button to register the payment.
        context_make_payment = {"active_ids": [self.pos_order_pos1.id], "active_id": self.pos_order_pos1.id}
        self.pos_make_payment = self.PosMakePayment.with_context(context_make_payment).create({
            'amount': self.pos_order_pos1.amount_total
        })
        context_payment = {'active_id': self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()
        gift_wallet_after = self.env["account.wallet"].search([("wallet_type_id", "=", self.gift_wallet_type.id)]) - gift_wallet_before
        # The wallet is created after payment
        self.assertEqual(
            1,
            len(gift_wallet_after),
        )

        # I check that the order is marked as paid and there is no invoice
        # attached to it
        self.assertEqual(self.pos_order_pos1.state, 'paid', "Order should be in paid state.")
        self.assertFalse(self.pos_order_pos1.account_move, 'Invoice should not be attached to order.')

        # I close the session to generate the journal entries
        current_session.action_pos_session_closing_control()
        gift_wallet_after = self.env["account.wallet"].search([("wallet_type_id", "=", self.gift_wallet_type.id)]) - gift_wallet_before
        self.assertEqual(
            450.0,
            gift_wallet_after.balance,
        )