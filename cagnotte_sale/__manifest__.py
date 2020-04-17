# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cagnotte Sale',
    'summary': """
        Allows to manage cagnotte on sale level""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'sale',
        'cagnotte_base',
        'cagnotte_partner',
    ],
    'data': [
        'security/security.xml',
        'views/account_cagnotte.xml',
        'views/sale_order.xml',
        'wizards/sale_cagnotte_pay.xml',
    ],
}
