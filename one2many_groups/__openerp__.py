# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of one2many_groups,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     one2many_groups is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     one2many_groups is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with one2many_groups.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "One2Many Groups",

    'summary': """
    TODO
    """,
    'author': "ACSONE SA/NV",
    'website': "http://acsone.eu",
    'category': 'Tools',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'base',
    ],
    'data': [
        "views/one2many_groups.xml",
    ],
    'qweb': [
        "static/src/xml/one2many_groups.xml",
    ],
}
