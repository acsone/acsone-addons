# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_sheet_invoice_approved,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_sheet_invoice_approved is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_sheet_invoice_approved is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_sheet_invoice_approved.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

SHEET_STATE_SELECTION = [('new', 'New'),
                         ('draft', 'Open'),
                         ('confirm', 'Waiting Approval'),
                         ('done', 'Approved')]


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    hr_analytic_timesheet_ids = fields.One2many(
        comodel_name='hr.analytic.timesheet', inverse_name='line_id',
        string='Timesheet Line')
    is_timesheet_line = fields.Boolean(compute='_is_timesheet_line',
                                       store=True)
    sheet_approved = fields.Boolean(compute='_get_sheet_approved',
                                    store=True)

    @api.one
    @api.depends('hr_analytic_timesheet_ids',
                 'hr_analytic_timesheet_ids.sheet_id',
                 'hr_analytic_timesheet_ids.sheet_id.state')
    def _get_sheet_approved(self):
        if self.is_timesheet_line and\
                self.hr_analytic_timesheet_ids.sheet_id.id and\
                self.hr_analytic_timesheet_ids.sheet_id.state == 'done':
            self.sheet_approved = True
        else:
            self.sheet_approved = False

    @api.one
    @api.depends('hr_analytic_timesheet_ids')
    def _is_timesheet_line(self):
        if self.hr_analytic_timesheet_ids.ids:
            self.is_timesheet_line = True
        else:
            self.is_timesheet_line = False
