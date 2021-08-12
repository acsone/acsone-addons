# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Wallet Delivery',
    'summary': """
        Adds logic when delivery rules are applied""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://gitub.com/OCA/account-wallet',
    'depends': [
        'account_wallet_sale',
        'delivery',
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/sale_order.xml",
    ]
}
