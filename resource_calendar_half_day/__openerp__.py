# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of resource_calendar_half_day,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     resource_calendar_half_day is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     resource_calendar_half_day is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with resource_calendar_half_day.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Resource calendar half day",

    'summary': """
        Allow to define half day in calendar""",
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
