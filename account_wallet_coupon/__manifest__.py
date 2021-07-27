# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Wallet Coupon",
    "version": "14.0.1.0.0",
    'author': "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account_wallet",
    "depends": [
        "account_wallet",
        "coupon",
    ],
    "data": [
        "views/account_wallet.xml",
        "views/account_wallet_type.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "post_init_hook",
}
