# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import datetime


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    state = fields.Selection(
        track_visibility='onchange',
    )

    @api.model
    def _convert_dates(self, date_from, date_to):
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        return (from_dt, to_dt)

    @api.model
    def _get_next_sunday_or_end_of_month(self, dt):
        ndt = dt + datetime.timedelta(days=6 - dt.weekday())
        if ndt.month != dt.month:
            ndt = datetime.datetime(
                ndt.year, ndt.month, 1) - datetime.timedelta(days=1)
        return ndt

    @api.onchange('date_from')
    def _onchange_date_period_from(self):
        from_dt, _ = self._convert_dates(self.date_from, self.date_to)
        # propose a new to date
        to_dt = self._get_next_sunday_or_end_of_month(from_dt)
        self.date_from = from_dt
        self.date_to = to_dt
