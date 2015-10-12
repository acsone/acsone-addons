# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of resource_calendar_multi_week,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     resource_calendar_multi_week is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     resource_calendar_multi_week is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with resource_calendar_multi_week.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields

WEEK_SELECTION = [('1', 'Week 1'),
                  ('2', 'Week 2')]


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    use_multi_week = fields.Boolean(string='Schedule of two weeks')
    first_week_date_start = fields.Date(string='Start Date of the first week')
    multi_week_attendance_ids = fields.One2many(
        comodel_name='resource.calendar.attendance',
        inverse_name='calendar_id', string='Working Time', copy=True)


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    week = fields.Selection(
        selection=WEEK_SELECTION, string='Week', required=True, default='1')
