# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos Account Wallet Coupon No Negative",
    "summary": """
        Glue module to manage no negative Wallets feature on POS side""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://acsone.eu",
    "depends": [
        "pos_account_wallet_coupon",
        "account_wallet_no_negative",
    ],
    "data": [
        "views/pos_template.xml",
    ],
    "auto_install": True,
}
