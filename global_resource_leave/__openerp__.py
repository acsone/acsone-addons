# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of global_resource_leave,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     global_resource_leave is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     global_resource_leave is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with global_resource_leave.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Global Resource Leave",

    'summary': """
        Define globals leaves for working times.
        """,
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Other',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'resource',
    ],
    'data': [
        'views/resource_view.xml',
    ],
}
