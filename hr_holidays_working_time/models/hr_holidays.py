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
from datetime import datetime
from dateutil import rrule


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    number_of_hours_temp = fields.Float('Allocation Hours')
    number_of_hours = fields.Float(
        'Allocation Hours', compute='_compute_number_of_hours', store=True)
    number_of_days_temp = fields.Float(
        compute='_compute_number_of_hours_from_hours', store=True)

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
            if employee.id and employee.current_contract_id.id and\
                    employee.current_contract_id.working_hours.id:
                working_time = employee.current_contract_id.working_hours
                start_dt = datetime.strptime(date_from,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                end_dt = datetime.strptime(date_to,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
                return working_time.get_working_hours(
                    start_dt, end_dt, compute_leaves=True, resource_id=None,
                    default_interval=None)[0]
        return False

    @api.multi
    def onchange_date_from(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_from(date_to, date_from)
        if date_from and not date_to:
            date_to = res['value']['date_to']
        if (date_to and date_from) and (date_from <= date_to):
            employee_id = self.env.context.get('employee_id', False)
            duration = self._get_duration_from_working_time(date_to, date_from,
                                                            employee_id)
            res['value']['number_of_hours_temp'] = duration
        return res

    @api.multi
    def onchange_date_to(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_to(date_to, date_from)
        if (date_to and date_from) and (date_from <= date_to):
            employee_id = self.env.context.get('employee_id', False)
            duration = self._get_duration_from_working_time(date_to, date_from,
                                                            employee_id)
            res['value']['number_of_hours_temp'] = duration
        return res
