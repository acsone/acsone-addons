# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from dateutil import rrule

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

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
    def get_attendances_for_weekday(self, day_dt):
        self.ensure_one()
        res = super(ResourceCalendar, self)\
            .get_attendances_for_weekday(day_dt)
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
        return res


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    week = fields.Selection(
        selection=WEEK_SELECTION, string='Week', required=True, default='1')
