# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Wallet No Negative",
    "summary": """
        Allows to set a limit on wallet use""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/acsone/acsone-addons",
    "depends": [
        "account_wallet",
    ],
    "data": [
        "views/account_wallet_type.xml",
        "views/account_wallet.xml",
    ],
    "installable": False,
}
