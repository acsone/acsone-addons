# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil import rrule


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    number_of_hours_temp = fields.Float(
        string='Allocation Hours', compute='_compute_number_of_hours_temp',
        store=True)
    number_of_hours = fields.Float(
        'Number of Hours', compute='_compute_number_of_hours', store=True,
        track_visibility='onchange')
    number_of_days_temp = fields.Float(
        compute='_compute_number_of_hours_from_hours', store=True,
        required=False, readonly=True)
    number_of_hours_temp_manual = fields.Float(string='Allocation Hours')
    set_hours_manually = fields.Boolean(track_visibility='onchange')

    @api.model
    def default_get(self, fields_list):
        res = super(HrHolidays, self).default_get(fields_list)
        if res.get('type', '') == 'add':
            res['set_hours_manually'] = True
        return res

    @api.model
    def _get_day_to_hours_factor(self):
        return 8.0

    @api.one
    @api.depends('number_of_hours_temp')
    def _compute_number_of_hours_from_hours(self):
        if self.number_of_hours_temp:
            self.number_of_days_temp = \
                self.number_of_hours_temp / self._get_day_to_hours_factor()
        else:
            self.number_of_days_temp = 0

    @api.one
    @api.depends('type', 'number_of_hours_temp')
    def _compute_number_of_hours(self):
        if self.type == 'remove':
            self.number_of_hours = - self.number_of_hours_temp
        else:
            self.number_of_hours = self.number_of_hours_temp

    @api.multi
    @api.depends('date_to', 'date_from', 'employee_id',
                 'number_of_hours_temp_manual', 'set_hours_manually')
    def _compute_number_of_hours_temp(self):
        for record in self:
            if not record.set_hours_manually:
                if record.date_to and record.date_from and\
                        record.date_from <= record.date_to:
                    record.number_of_hours_temp =\
                        record._get_duration_from_working_time(
                            record.date_to, record.date_from,
                            record.employee_id)
            else:
                record.number_of_hours_temp =\
                    record.number_of_hours_temp_manual

    @api.model
    def _no_current_contract(self, day):
        return False

    @api.model
    def _no_working_time(self, day):
        return False

    @api.multi
    def _get_duration_from_working_time(self, date_to, date_from, employee):
        if employee:
            if employee.id:
                contract_obj = self.env['hr.contract']
                start_dt = datetime.strptime(date_from,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                end_dt = datetime.strptime(date_to,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
                hours = 0.0
                for day in rrule.rrule(
                        rrule.DAILY, dtstart=start_dt,
                        until=(end_dt + timedelta(days=1))
                        .replace(hour=0, minute=0, second=0),
                        byweekday=[0, 1, 2, 3, 4, 5, 6]):
                    day_start_dt = day.replace(hour=0, minute=0, second=0)
                    day_str = fields.Date.to_string(day_start_dt)
                    current_contract_id =\
                        employee.sudo()._get_current_contract(day_str)
                    if not current_contract_id:
                        if not self._no_current_contract(day_str):
                            continue
                    current_contract =\
                        contract_obj.sudo().browse([current_contract_id])
                    working_time = current_contract.working_hours
                    if not working_time.id:
                        if not self._no_working_time(day_str):
                            continue
                    if start_dt and day.date() == start_dt.date():
                        day_start_dt = start_dt
                    day_end_dt = day.replace(hour=23, minute=59, second=59)
                    if end_dt and day.date() == end_dt.date():
                        day_end_dt = end_dt
                    hours += working_time.get_working_hours_of_date(
                        start_dt=day_start_dt, end_dt=day_end_dt,
                        compute_leaves=True, resource_id=None,
                        default_interval=None)
                return hours
        return False

    @api.model
    def _prepare_create_by_category(self, record, employee):
        res = super(HrHolidays, self)._prepare_create_by_category(
            record, employee)
        res['set_hours_manually'] = True
        res['number_of_hours_temp_manual'] = record.number_of_hours_temp_manual
        return res
