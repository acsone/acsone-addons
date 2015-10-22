# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_working_time,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_working_time is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_working_time is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_working_time.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,\
    DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp import fields
import pytz


def create_resource_leave(self, date_from, date_to, calendar_id):
    vals = {
        'name': 'Test',
        'date_from': date_from,
        'date_to': date_to,
        'calendar_id': calendar_id,
        'resource_id': False,
    }
    return self.env['resource.calendar.leaves'].create(vals)


def create_full_working_time(self):
    vals = {
        'name': 'Test Full Time',
        'attendance_ids': [(0, 0, {'name': 'Test0',
                                   'dayofweek': '0',
                                   'periodofday': 'morning',
                                   'hour_from': 8,
                                   'hour_to': 12}),
                           (0, 0, {'name': 'Test1',
                                   'dayofweek': '1',
                                   'periodofday': 'morning',
                                   'hour_from': 8,
                                   'hour_to': 12}),
                           (0, 0, {'name': 'Test2',
                                   'dayofweek': '2',
                                   'periodofday': 'morning',
                                   'hour_from': 8,
                                   'hour_to': 12}),
                           (0, 0, {'name': 'Test3',
                                   'dayofweek': '3',
                                   'periodofday': 'morning',
                                   'hour_from': 8,
                                   'hour_to': 12}),
                           (0, 0, {'name': 'Test4',
                                   'dayofweek': '4',
                                   'periodofday': 'morning',
                                   'hour_from': 8,
                                   'hour_to': 12}),
                           (0, 0, {'name': 'Test0',
                                   'dayofweek': '0',
                                   'periodofday': 'afternoon',
                                   'hour_from': 13,
                                   'hour_to': 17}),
                           (0, 0, {'name': 'Test1',
                                   'dayofweek': '1',
                                   'periodofday': 'afternoon',
                                   'hour_from': 13,
                                   'hour_to': 17}),
                           (0, 0, {'name': 'Test2',
                                   'dayofweek': '2',
                                   'periodofday': 'afternoon',
                                   'hour_from': 13,
                                   'hour_to': 17}),
                           (0, 0, {'name': 'Test3',
                                   'dayofweek': '3',
                                   'periodofday': 'afternoon',
                                   'hour_from': 13,
                                   'hour_to': 17}),
                           (0, 0, {'name': 'Test4',
                                   'dayofweek': '4',
                                   'periodofday': 'afternoon',
                                   'hour_from': 13,
                                   'hour_to': 17})]
    }
    return self.calendar_obj.create(vals)


class TestHrHolidaysWorkingTime(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysWorkingTime, self).setUp()
        self.calendar_obj = self.env['resource.calendar']
        self.today = datetime.now()
        # Get the first day of the current week
        self.first_day_start_dt =\
            self.today - timedelta(days=self.today.weekday())
        self.working_time01 = create_full_working_time(self)
        self._context = self.env['res.users'].context_get()

    def test_holidays_working_time_one_day(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt.replace(hour=17, minute=0,
                                                     second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)[0]
        self.assertAlmostEqual(hours, 8, 2)

    def test_holidays_working_time_complete_week(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=4)
        date_to_dt = date_to_dt.replace(hour=17, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)[0]
        self.assertAlmostEqual(hours, 40, 2)

    def test_holidays_working_time_weekend(self):
        date_from_dt = self.first_day_start_dt + timedelta(days=5)
        date_from_dt = date_from_dt.replace(hour=8, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=6)
        date_to_dt = date_to_dt.replace(hour=17, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)[0]
        self.assertAlmostEqual(hours, 0, 2)

    def test_holidays_working_time_leave(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt.replace(hour=17, minute=0,
                                                     second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_from = date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # I create a resource leave
        create_resource_leave(self, date_from, date_to, self.working_time01.id)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)[0]
        self.assertAlmostEqual(hours, 0, 2)
