# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .common import WalletCommon
from psycopg2 import IntegrityError
from odoo.tools import mute_logger


class TestWallet(WalletCommon):

    def test_wallet(self):
        """ Buy wallet product
            Check wallet amount
            Pay with wallet
            Check wallet amount
            Try to pay with more than available
            Check error
        """
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)
        invoice = self.env["account.move"].create({
            'move_type': 'out_invoice',
            'partner_id': self.env.ref("base.res_partner_2").id,
            'invoice_line_ids': [(0, 0, {
                'name': 'set 100 in my wallet',
                'quantity': 1,
                'price_unit': 100,
                'product_id': self.wallet_type.product_id.id,
                'account_id': self.wallet_type.account_id.id,
            })],
        })
        invoice.action_post()
        has_wallet = False
        for line in invoice.invoice_line_ids:
            if line.account_id.id == self.wallet_type.account_id.id:
                wallet = line.account_wallet_id
                self.assertTrue(wallet.wallet_type_id.id,
                                self.wallet_type.id)
                has_wallet = True
        self.assertTrue(has_wallet)
        self.assertAlmostEqual(wallet.balance, 100.00, 2)

        move_obj = self.env["account.move"]

        move_obj.create(
            {"journal_id": wallet.wallet_type_id.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": wallet.wallet_type_id.account_id.id,
                     "account_wallet_id": wallet.id,
                     "name": "payment with my wallet",
                     "debit": 100
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "payment with my wallet",
                     "credit": 100})]})
        self.assertEqual(len(wallet.account_move_line_ids), 2)
        self.assertAlmostEqual(wallet.balance, 0.00, 2)

    def test_wallet_partner(self):
        """ Create wallet with partner
            Use wallet
            check partner is on account move
        """
        self.wallet.partner_id = self.partner
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)

        move_obj = self.env["account.move"]

        wallet_move = move_obj.create({
            "journal_id": self.wallet_type.journal_id.id,
            "line_ids": [
                (0, 0, {
                    "account_id": self.wallet_type.account_id.id,
                    "account_wallet_id": self.wallet.id,
                    "name": "get credit on my wallet",
                    "credit": 100
                }),
                (0, 0, {
                    "account_id": invoice_account.id,
                    "name": "get credit on my wallet",
                    "debit": 100})]})

        line = self.env['account.move.line'].search([
            ('move_id', '=', wallet_move.id),
            ('credit', '=', 100)
        ])
        self.assertEqual(line.partner_id.id, self.partner.id)
        self.assertAlmostEqual(self.wallet.balance, 100.00, 2)

        move_obj.create(
            {"journal_id": self.wallet_type.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": self.wallet_type.account_id.id,
                     "partner_id": self.partner.id,
                     "account_wallet_id": self.wallet.id,
                     "name": "payement with my wallet",
                     "debit": 20
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "payement with my wallet",
                     "credit": 20})]})

        self.assertAlmostEqual(self.wallet.balance, 80.00, 2)

    @mute_logger("odoo.sql_db")
    def test_wallet_unique(self):
        self.wallet.partner_id = self.partner
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.wallet_obj.create(
                {'wallet_type_id': self.wallet_type.id,
                 'partner_id': self.partner.id})

        wallet_2 = self.wallet_obj.create(
            {'wallet_type_id': self.wallet_type.id,
             'partner_id': self.partner.id,
             'active': False})

        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            wallet_2.write({'active': True})

        self.wallet.write({'active': False})
