# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,\
    DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo import fields
import pytz


def create_simple_contract(self, employee, date_start, date_end=False):
    vals = {
        'name': 'Test',
        'employee_id': employee.id,
        'date_start': date_start,
        'date_end': date_end,
        'wage': 1.0,
    }
    return self.contract_obj.create(vals)


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
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test1',
                                   'dayofweek': '1',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test2',
                                   'dayofweek': '2',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test3',
                                   'dayofweek': '3',
                                   'hour_from': 8,
                                   'hour_to': 16}),
                           (0, 0, {'name': 'Test4',
                                   'dayofweek': '4',
                                   'hour_from': 8,
                                   'hour_to': 16})]
    }
    return self.calendar_obj.create(vals)


def create_leave(self, date_from, date_to, employee):
    vals = {
        'employee_id': employee.id,
        'date_from': date_from,
        'date_to': date_to,
        'holiday_status_id': self.env.ref('hr_holidays.holiday_status_sl').id
    }
    return self.holidays_obj.create(vals)


class TestHrHolidaysWorkingTime(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysWorkingTime, self).setUp()
        self.holidays_obj = self.env['hr.holidays']
        self.employee_obj = self.env['hr.employee']
        self.contract_obj = self.env['hr.contract']
        self.calendar_obj = self.env['resource.calendar']
        self.employee01 = self.env.ref('hr.employee_vad')
        self.today = datetime.now()
        # Get the first day of the current week
        self.first_day_start_dt =\
            self.today - timedelta(days=self.today.weekday())
        self.contract01 = create_simple_contract(
            self, self.employee01, self.first_day_start_dt)
        self.working_time01 = create_full_working_time(self)
        self.contract01.working_hours = self.working_time01
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
        date_from = date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        holiday = create_leave(self, date_from, date_to, self.employee01)
        self.assertEqual(holiday.number_of_hours_temp, 8)

    def test_holidays_working_time_complete_week(self):
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
        date_from = date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        holiday = create_leave(self, date_from, date_to, self.employee01)
        self.assertEqual(holiday.number_of_hours_temp, 40)

    def test_holidays_working_time_weekend(self):
        date_from_dt = self.first_day_start_dt + timedelta(days=5)
        date_from_dt = date_from_dt.replace(hour=8, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_from_dt).tzinfo
        date_from_dt = date_from_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_to_dt = self.first_day_start_dt + timedelta(days=6)
        date_to_dt = date_to_dt.replace(hour=16, minute=0, second=0)
        tz_info = fields.Datetime.context_timestamp(self, date_to_dt).tzinfo
        date_to_dt = date_to_dt.replace(tzinfo=tz_info)\
            .astimezone(pytz.UTC).replace(tzinfo=None)
        date_from = date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        holiday = create_leave(self, date_from, date_to, self.employee01)
        self.assertEqual(holiday.number_of_hours_temp, 0)

    def test_holidays_working_time_leave(self):
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
        date_from = date_from_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = date_to_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # I create a resource leave
        create_resource_leave(self, date_from, date_to, self.working_time01.id)
        holiday = create_leave(self, date_from, date_to, self.employee01)
        self.assertEqual(holiday.number_of_hours_temp, 0)
