# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_details_report,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_details_report is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_details_report is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_details_report.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, timedelta
from openerp import models, fields, api, exceptions


class HrTimesheetDetailsReportWizard(models.TransientModel):
    _name = 'hr.timesheet.details.report.wizard'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    user_id = fields.Many2one('res.users', 'User', required=True)
    period_start = fields.Date("Start date", required=True)
    period_end = fields.Date("End date", required=True)
    project_ids = fields.Many2many(
        comodel_name='project.project',
        relation='hr_ts_detail_project_user_rel', column1='project_id',
        column2='uid', string='Projects')
    total_hours = fields.Float()

    @api.one
    @api.onchange('employee_id')
    def on_change_employee_id(self):
        if self.employee_id:
            self.user_id = self.employee_id.user_id.id

    @api.model
    def _get_emp_user(self):
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', self._uid)])
        if not emp_id:
            raise exceptions.Warning(_("No employee defined for this user"))
        return emp_id.id, emp_id.user_id.id

    @api.model
    def default_get(self, fields):
        res = {}
        res['employee_id'], res['user_id'] = self._get_emp_user()
        date_end =\
            date(date.today().year, date.today().month, 1) - timedelta(days=1)
        date_start = date(date_end.year, date_end.month, 1)
        res['period_start'] = date_start.strftime("%Y-%m-%d")
        res['period_end'] = date_end.strftime("%Y-%m-%d")
        return res

    @api.multi
    def run(self):
        self.ensure_one()
        data = self.read(HrTimesheetDetailsReportWizard._columns.keys())[0]
        report_name =\
            'hr_timesheet_details_report.hr_timesheet_details_report'
        return {'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data}
