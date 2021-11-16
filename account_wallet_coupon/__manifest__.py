# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Wallet Coupon",
    "version": "14.0.1.0.1",
    "author": "ACSONE SA/NV",
    "category": "Accounting & Finance",
    "website": "https://acsone.eu",
    "depends": [
        "account_wallet",
        "coupon",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "data": [
        "wizards/account_payment_register.xml",
        "security/security.xml",
        "views/account_wallet.xml",
        "views/account_wallet_type.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "post_init_hook": "post_init_hook",
}
