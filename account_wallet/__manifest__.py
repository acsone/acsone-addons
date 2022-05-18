# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Wallet",
    "version": "14.0.1.0.2",
    "author": "ACSONE SA/NV",
    "category": "Accounting & Finance",
    "website": "https://github.com/acsone/acsone-addons",
    "depends": [
        "account",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "data": [
        "security/security.xml",
        "security/wallet_base_security.xml",
        "views/wallet_views.xml",
        "views/wallet_type.xml",
        "views/account_move_line.xml",
        "views/account_move.xml",
        "views/res_partner.xml",
        "wizards/wizard_account_move_refund_wallet.xml",
    ],
    "license": "AGPL-3",
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
