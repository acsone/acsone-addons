# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cagnotte Sale Display Discount Amount',
    'summary': """
        Allows to take into account cagnotte in discounts""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'cagnotte_sale',
        'sale_discount_display_amount',
    ],
    'auto_install': True,
}
