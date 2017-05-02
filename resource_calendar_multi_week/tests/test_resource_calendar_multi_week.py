# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz

from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
from odoo import fields


def create_resource_leave(self, date_from, date_to, calendar_id):
    vals = {
        'name': 'Test',
        'date_from': date_from,
        'date_to': date_to,
        'calendar_id': calendar_id,
        'resource_id': False,
    }
    return self.env['resource.calendar.leaves'].create(vals)


def create_full_working_time(self, start_week_dt):
    vals = {
        'name': 'Test Full Time',
        'use_multi_week': True,
        'first_week_date_start': start_week_dt
        .strftime(DEFAULT_SERVER_DATE_FORMAT),
        'attendance_ids': [(0, 0, {'name': 'Test0',
                                   'dayofweek': '0',
                                   'week': '2',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test1',
                                   'dayofweek': '1',
                                   'week': '2',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test2',
                                   'dayofweek': '2',
                                   'week': '1',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test3',
                                   'dayofweek': '3',
                                   'week': '1',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test4',
                                   'dayofweek': '4',
                                   'week': '1',
                                   'hour_from': 8,
                                   'hour_to': 16})]
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
        self.working_time01 = create_full_working_time(self,
                                                       self.first_day_start_dt)
        self._context = self.env['res.users'].context_get()

    def test_holidays_working_time_one_day(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt.replace(hour=16, minute=0,
                                                     second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)
        self.assertAlmostEqual(hours, 0, 2)

    def test_holidays_working_time_first_week(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=4)
        date_to_dt = date_to_dt.replace(hour=16, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)
        self.assertAlmostEqual(hours, 24, 2)

    def test_holidays_working_time_first_week_one_day(self):
        date_from_dt = self.first_day_start_dt.replace(hour=8, minute=0,
                                                       second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=7)
        date_to_dt = date_to_dt.replace(hour=16, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)
        self.assertAlmostEqual(hours, 32, 2)

    def test_holidays_working_time_second_week(self):
        date_from_dt = self.first_day_start_dt + timedelta(days=7)
        date_from_dt = date_from_dt.replace(hour=8, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=11)
        date_to_dt = date_to_dt.replace(hour=16, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)
        self.assertAlmostEqual(hours, 16, 2)

    def test_holidays_working_time_two_week(self):
        date_from_dt = self.first_day_start_dt
        date_from_dt = date_from_dt.replace(hour=8, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=11)
        date_to_dt = date_to_dt.replace(hour=16, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        hours = self.working_time01.get_working_hours(
            date_from_dt, date_to_dt, compute_leaves=True, resource_id=None,
            default_interval=None)
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
            default_interval=None)
        self.assertAlmostEqual(hours, 0, 2)
