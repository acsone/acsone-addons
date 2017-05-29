# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_sheet_usability,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_sheet_usability is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_sheet_usability is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_sheet_usability.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import datetime


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    state = fields.Selection(track_visibility='onchange')

    @api.model
    def convert_dates(self, date_from, date_to):
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        return (from_dt, to_dt)

    @api.model
    def get_next_sunday_or_end_of_month(self, dt):
        ndt = dt + datetime.timedelta(days=6-dt.weekday())
        if ndt.month != dt.month:
            ndt = datetime.datetime(
                ndt.year, ndt.month, 1) - datetime.timedelta(days=1)
        return ndt

    @api.one
    @api.onchange('date_from')
    def on_change_date_period_from(self):
        from_dt, _ = self.convert_dates(self.date_from, self.date_to)
        # propose a new to date
        to_dt = self.get_next_sunday_or_end_of_month(from_dt)
        self.date_from = fields.Date.to_string(from_dt)
        self.date_to = fields.Date.to_string(to_dt)


class hr_analytic_timesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.one
    @api.onchange('date')
    def on_change_date_in_details(self):
        """ Coerce date within timesheet period """
        date_from = self.env.context.get('timesheet_date_from', False)
        date_to = self.env.context.get('timesheet_date_to', False)
        if self.date and date_from and date_to:
            if self.date < date_from:
                self.date = date_from
            if self.date > date_to:
                self.date = date_to
