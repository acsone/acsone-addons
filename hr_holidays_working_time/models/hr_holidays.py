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

from openerp import models, api, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil import rrule


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.cr_context
    def _auto_init(self, cr, context=None):
        """ hack: pre-create and initialize the columns so that the
        constraint setting will not fail, this is a hack, made necessary
        because Odoo tries to set the not-null constraint before
        applying default values """
        self._field_create(cr, context=context)
        column_data = self._select_column_data(cr)
        cr.execute("""SELECT demo FROM ir_module_module WHERE name=%s""",
                   ('base',))
        demo = cr.fetchone()
        if isinstance(demo, tuple) and demo[0]:
            if 'number_of_hours_temp' not in column_data:
                cr.execute('ALTER TABLE "{table}" ADD COLUMN "number_of_hours_temp" numeric'.
                           format(table=self._table))
                cr.execute('UPDATE "{table}" SET number_of_hours_temp=number_of_days_temp*8'.
                           format(table=self._table), ())
        return super(HrHolidays, self)._auto_init(cr, context=context)

    number_of_hours_temp = fields.Float('Allocation Hours')
    number_of_hours = fields.Float(
        'Number of Hours', compute='_compute_number_of_hours', store=True)
    number_of_days_temp = fields.Float(
        compute='_compute_number_of_hours_from_hours', store=True)

    _sql_constraints = [
        ('date_check3_hours', "CHECK ( number_of_hours_temp > 0 )",  "The number of hours must be greater than 0.")
    ]

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
    def _get_duration_from_working_time(self, date_to, date_from, employee_id):
        if employee_id:
            employee = self.env['hr.employee'].sudo().browse([employee_id])
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
                        continue
                    current_contract =\
                        contract_obj.sudo().browse([current_contract_id])
                    working_time = current_contract.working_hours
                    if not working_time.id:
                        continue
                    if start_dt and day.date() == start_dt.date():
                        day_start_dt = start_dt
                    day_end_dt = day.replace(hour=23, minute=59, second=59)
                    if end_dt and day.date() == end_dt.date():
                        day_end_dt = end_dt
                    hours += working_time.get_working_hours_of_date(
                        start_dt=day_start_dt, end_dt=day_end_dt,
                        compute_leaves=True, resource_id=None,
                        default_interval=None)[0]
                return hours
        return False

    @api.multi
    def onchange_employee(self, employee_id):
        res = super(HrHolidays, self).onchange_employee(employee_id)
        date_from = self.env.context.get('date_from')
        date_to = self.env.context.get('date_to')
        if (date_to and date_from) and (date_from <= date_to):
            duration = self._get_duration_from_working_time(
                date_to, date_from, employee_id)
            res['value']['number_of_hours_temp'] = duration
        return res

    @api.multi
    def onchange_date_from(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_from(date_to, date_from)
        if date_from and not date_to:
            date_to = res['value']['date_to']
        if (date_to and date_from) and (date_from <= date_to):
            employee_id = self.env.context.get('employee_id', False)
            if employee_id:
                duration = self._get_duration_from_working_time(
                    date_to, date_from, employee_id)
                res['value']['number_of_hours_temp'] = duration
        return res

    @api.multi
    def onchange_date_to(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_to(date_to, date_from)
        if (date_to and date_from) and (date_from <= date_to):
            employee_id = self.env.context.get('employee_id', False)
            if employee_id:
                duration = self._get_duration_from_working_time(
                    date_to, date_from, employee_id)
                res['value']['number_of_hours_temp'] = duration
        return res
