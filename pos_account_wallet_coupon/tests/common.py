# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_wallet.tests.common import WalletCommon


class PosWalletCommon(WalletCommon):
    @classmethod
    def compute_tax(cls, product, price, qty=1, taxes=None):
        if not taxes:
            taxes = product.taxes_id.filtered(
                lambda t: t.company_id.id == cls.env.company.id
            )
        currency = cls.pos_config.pricelist_id.currency_id
        res = taxes.compute_all(price, currency, qty, product=product)
        untax = res["total_excluded"]
        return untax, sum(tax.get("amount", 0.0) for tax in res["taxes"])

    @classmethod
    def _create_gift_wallet_type(cls):
        vals = {
            "name": "Current Gift Wallets",
            "user_type_id": cls.env.ref("account.data_account_type_prepayments").id,
            "code": "CURGIF",
        }
        cls.temp_account = cls.account_obj.create(vals)
        vals = {
            "name": "Customer Wallet Gift Type",
            "code": "account.wallet",
            "padding": 5,
            "prefix": "WALG",
            "company_id": cls.env.ref("base.main_company").id,
        }
        cls.sequence_gift = cls.env["ir.sequence"].create(vals)
        vals = {
            "name": "Gift Product",
            "property_account_income_id": cls.temp_account.id,
            "property_account_expense_id": cls.temp_account.id,
        }
        cls.gift_product = cls.env["product.product"].create(vals)
        vals = {
            "name": "Gift Wallet Account",
            "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            "code": "GIFAC",
        }
        cls.gift_account = cls.account_obj.create(vals)
        vals = {
            "name": "Gift Wallet Journal",
            "code": "WALJOU",
            "type": "cash",
            "default_account_id": cls.temp_account.id,
        }
        cls.gift_journal = cls.journal_obj.create(vals)
        vals = {
            "name": "Gift Wallet",
            "journal_id": cls.gift_journal.id,
            "account_id": cls.temp_account.id,
            "sequence_id": cls.sequence_gift.id,
            "product_id": cls.gift_product.id,
        }
        cls.gift_wallet_type = cls.wallet_type_obj.create(vals)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_user = cls.env.ref("base.user_demo")
        cls.AccountBankStatement = cls.env["account.bank.statement"]
        cls.AccountBankStatementLine = cls.env["account.bank.statement.line"]
        cls.PosMakePayment = cls.env["pos.make.payment"]
        cls.PosOrder = cls.env["pos.order"]
        cls.PosSession = cls.env["pos.session"]
        cls.account_obj = cls.env["account.account"]
        cls.journal_obj = cls.env["account.journal"]
        cls.company = cls.env.ref("base.main_company")
        cls.wallet_type_obj = cls.env["account.wallet.type"]
        cls.sale_journal = cls.journal_obj.search([("type", "=", "sale")], limit=1)
        cls.cash_journal = cls.journal_obj.search([("type", "=", "cash")], limit=1)
        cls.bank_journal = cls.journal_obj.search([("type", "=", "bank")], limit=1)
        cls.pos_receivable_account = (
            cls.company.account_default_pos_receivable_account_id
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "list_price": 450,
            }
        )
        cls.product4 = cls.env["product.product"].create(
            {
                "name": "Product 4",
                "list_price": 750,
            }
        )
        cls.partner1 = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.partner4 = cls.env["res.partner"].create({"name": "Partner 4"})
        cls.pos_config = cls.env["pos.config"].create(
            {
                "name": "Main",
                "journal_id": cls.sale_journal.id,
                "invoice_journal_id": cls.sale_journal.id,
            }
        )
        cls.led_lamp = cls.env["product.product"].create(
            {
                "name": "LED Lamp",
                "available_in_pos": True,
                "list_price": 0.90,
            }
        )
        cls.whiteboard_pen = cls.env["product.product"].create(
            {
                "name": "Whiteboard Pen",
                "available_in_pos": True,
                "list_price": 1.20,
            }
        )
        cls.newspaper_rack = cls.env["product.product"].create(
            {
                "name": "Newspaper Rack",
                "available_in_pos": True,
                "list_price": 1.28,
            }
        )
        cls.cash_payment_method = cls.env["pos.payment.method"].create(
            {
                "name": "Cash",
                "receivable_account_id": cls.pos_receivable_account.id,
                "is_cash_count": True,
                "cash_journal_id": cls.cash_journal.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.bank_payment_method = cls.env["pos.payment.method"].create(
            {
                "name": "Bank",
                "receivable_account_id": cls.pos_receivable_account.id,
                "is_cash_count": False,
                "company_id": cls.env.company.id,
            }
        )
        cls.wallet_journal.write({"is_wallet_with_coupon": True})
        cls.wallet_payment_method = cls.env["pos.payment.method"].create(
            {
                "name": "Wallet",
                "receivable_account_id": cls.pos_receivable_account.id,
                "is_cash_count": True,
                "cash_journal_id": cls.wallet_journal.id,
                "company_id": cls.env.company.id,
                "split_transactions": True,
            }
        )
        cls.pos_config.write(
            {
                "payment_method_ids": [
                    (4, cls.wallet_payment_method.id),
                    (4, cls.bank_payment_method.id),
                    (4, cls.cash_payment_method.id),
                ]
            }
        )

        # Create POS journal
        cls.pos_config.journal_id = cls.env["account.journal"].create(
            {
                "type": "sale",
                "name": "Point of Sale - Test",
                "code": "POSS - Test",
                "company_id": cls.env.company.id,
                "sequence": 20,
            }
        )

        vals = {
            "wallet_type_id": cls.wallet_type.id,
        }
        cls.wallet_2 = cls.wallet_obj.create(vals)
