# -*- coding: utf-8 -*-
# Copyright © 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Easy Debug Backend',
    'version': '9.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Other',
    'depends': [
        'base',
        'web',
    ],
    'description': """
Easy Debug Backend
==================
Constantly apply 'debug mode' for backend
""",
    'data': [
        'views/easy_debug_backend.xml',
    ],
    'installable': True,
    'auto_install': False,
}
