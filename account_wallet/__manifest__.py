# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Wallet",
    "version": "14.0.1.0.0",
    'author': "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/",
    "depends": [
        "account",
    ],
    "data": [
        "security/security.xml",
        "security/wallet_base_security.xml",
        "views/wallet_views.xml",
        "views/wallet_type.xml",
        "views/account_move_line.xml",
        "views/account_move.xml",
        "views/res_partner.xml",
    ],
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
}
