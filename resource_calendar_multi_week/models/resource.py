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

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import rrule
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

WEEK_SELECTION = [('1', 'Week 1'),
                  ('2', 'Week 2')]


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    use_multi_week = fields.Boolean(string='Schedule of two weeks')
    first_week_date_start = fields.Date(string='Start Date of the first week')
    multi_week_attendance_ids = fields.One2many(
        comodel_name='resource.calendar.attendance',
        inverse_name='calendar_id', string='Working Time', copy=True)

    @api.multi
    def get_attendances_for_weekdays(self, weekdays):
        self.ensure_one()
        res = super(ResourceCalendar, self)\
            .get_attendances_for_weekdays(weekdays)
        # To avoid to return a list of list due to old api signature in
        # standard addons
        if len(res) == 1 and isinstance(res[0], list):
                res = res[0]
        if self.env.context.get('date_multi_week') and self.use_multi_week:
            start_dt = datetime.strptime(self.first_week_date_start,
                                         DEFAULT_SERVER_DATE_FORMAT)
            current_dt = datetime.strptime(
                self.env.context.get('date_multi_week'),
                DEFAULT_SERVER_DATE_FORMAT)
            first_day_start_dt = start_dt - timedelta(days=start_dt.weekday())
            # Compute the number of week between the first week start date
            weeks = rrule.rrule(rrule.WEEKLY, dtstart=first_day_start_dt,
                                until=current_dt)
            str_week = str(((weeks.count()-1) % len(WEEK_SELECTION)) + 1)
            att_ids = []
            for att in res:
                if att.week == str_week:
                    att_ids.append(att)
            return att_ids
        else:
            return res

    @api.multi
    def get_working_intervals_of_day(self, start_dt=None, end_dt=None,
                                     leaves=None, compute_leaves=False,
                                     resource_id=None,
                                     default_interval=None):
        ctx = self.env.context.copy()
        if self.use_multi_week:
            ctx['date_multi_week'] =\
                start_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        res = super(ResourceCalendar, self.with_context(ctx))\
            .get_working_intervals_of_day(
            start_dt=start_dt, end_dt=end_dt, leaves=leaves,
            compute_leaves=compute_leaves, resource_id=resource_id,
            default_interval=default_interval)
        # To avoid to return a list of list due to old api signature in
        # standard addons
        if len(res) == 1 and isinstance(res[0], list):
                res = res[0]
        return res


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    week = fields.Selection(
        selection=WEEK_SELECTION, string='Week', required=True, default='1')
