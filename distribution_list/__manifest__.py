# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     distribution_list is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     distribution_list is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Distribution List',
    'version': '8.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'https://github.com/acsone/acsone-addons',
    'category': 'Marketing',
    'depends': [
        'base',
        'web',
        'email_template',
    ],
    'description': """
Distribution List
=================
This module provide features to allow the user to
* create distribution lists composed with dynamic filters (odoo domain)
* manage those distribution lists by adding or deleting lines
""",
    'images': [
        'static/src/img/icons/gtk-ey.png',
    ],
    'data': [
        'security/distribution_list_security.xml',
        'security/ir.model.access.csv',
        'distribution_list_view.xml',
        'wizard/distribution_list_add_filter_view.xml',
        'wizard/mail_compose_message_view.xml',
        'wizard/merge_distribution_list_view.xml',
        'data/email_template_data.xml',
    ],
    'qweb': [
        'static/src/xml/filter_selection.xml',
    ],
    'demo': [
        'demo/distribution_list_demo.xml',
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
    'auto_install': False,
}
