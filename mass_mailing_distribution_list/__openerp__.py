# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mass_mailing_distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mass_mailing_distribution_list is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mass_mailing_distribution_list is distributed
#     in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mass_mailing_distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Mass Mailing Distribution List',
    'version': '8.0.1.1.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'distribution_list',
        'mass_mailing',
    ],
    'description': """
Mass Mailing Distribution List
==============================

This module make a link between distribution list and mass mailing.

It allows:
* to declare a distribution list as a newsletter to also define
  static lists of partners (opt In/Out)
* to unsubscribe partner (i.e. add it to the opt Out list) through
  the unsubscribe link added to the mailing
* to receive an external mail and forward it to all recipients filtered by
  the distribution list
""",
    'images': [
    ],
    'data': [
        'views/mass_mailing.xml',
        'views/distribution_list_view.xml',
        'wizard/merge_distribution_list_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
