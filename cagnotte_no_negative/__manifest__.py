# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cagnotte Limit',
    'summary': """
        Allows to set a limit on cagnotte use""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        "cagnotte_base",
    ],
    "data": [
        "views/cagnotte_type.xml",
        "views/cagnotte.xml",
    ]
}
