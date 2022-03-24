# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError

from odoo.addons.account_wallet.tests.common import WalletCommon


class TestWalletNegative(WalletCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_model = cls.env["account.account"]
        cls.move_obj = cls.env["account.move"]
        cls.partner3 = cls.env.ref("base.res_partner_3")
        account_user_type = cls.env.ref("account.data_account_type_receivable")
        cls.account_rec1_id = cls.account_model.create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            )
        )
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        # Create a wallet type with no negative constraint
        cls.wallet_type.no_negative = True
        vals = {
            "wallet_type_id": cls.wallet_type.id,
        }
        wallet = cls.wallet_obj.new(vals)
        wallet._onchange_wallet_type_id()
        cls.wallet_no_negative = cls.wallet_obj.create(
            wallet._convert_to_write(wallet._cache)
        )

    def test_no_negative(self):
        """
        Provision wallet with 100.0
        Use wallet with 200.0
        """
        self._provision_wallet(100.0)
        account_id = self.wallet_no_negative.wallet_type_id.account_id.id
        journal_id = self.wallet_no_negative.wallet_type_id.journal_id.id
        vals = {
            "journal_id": journal_id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": account_id,
                        "account_wallet_id": self.wallet_no_negative.id,
                        "name": "payment with my wallet",
                        "debit": 100,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "account_id": self.account_rec1_id.id,
                        "name": "payment with my wallet",
                        "credit": 100,
                    },
                ),
            ],
        }
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.move_obj.create(vals)

        # Authorize negative wallet
        self.wallet_no_negative.no_negative = False
        self.move_obj.create(vals)
        self.assertTrue(self.wallet_no_negative.is_negative)

    def test_wallet_create_type(self):
        """
        Create a wallet from code specifying simply the type
        """
        vals = {
            "wallet_type_id": self.wallet_type.id,
        }
        wallet = self.wallet_obj.create(vals)
        self.assertTrue(wallet.no_negative)
