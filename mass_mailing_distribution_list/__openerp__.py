# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Mailing Distribution List',
    'summary':
        'This module make a link between distribution list and mass mailing.',
    'version': '8.0.1.1.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'distribution_list',
        'mass_mailing',
    ],
    'data': [
        'views/mass_mailing.xml',
        'views/distribution_list_view.xml',
        'wizard/merge_distribution_list_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
