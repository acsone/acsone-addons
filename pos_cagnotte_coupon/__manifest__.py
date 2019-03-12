# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "POS Cagnotte Coupon",
    'version': '10.0.1.0.0',
    'author': 'Acsone SA/NV',
    'category': "Point Of Sale,Accounting & Finance",
    'website': 'http://www.acsone.eu',
    'depends': [
        'cagnotte_coupon',
        'point_of_sale'
    ],
    'data': [
        'views/account_bank_statement.xml',
        'views/cagnotte_type.xml',
        'views/pos_order.xml',
        'views/pos_template.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
