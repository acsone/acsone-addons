# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_previous_month_filter,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_previous_month_filter is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_previous_month_filter is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_previous_month_filter.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "HR timesheet previous month filter",

    'summary': """
        Add filters for previous month for timesheet""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Human resources',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet',
        'account',
    ],
    'data': [
        'views/hr_analytic_timesheet_view.xml',
    ],
    'installable': False,
}
