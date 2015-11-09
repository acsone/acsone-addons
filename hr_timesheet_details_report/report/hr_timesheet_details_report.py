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

from openerp import api, models
import dateutil
from datetime import datetime
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class TSDetailReport(models.AbstractModel):
    _name = "report.hr_timesheet_details_report.hr_timesheet_details_report"

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        hr_analytic_timesheet = self.env['hr.analytic.timesheet']
        project_obj = self.env['project.project']

        user_name = data['employee_id'][1]
        user_lang_str = self.env.user.partner_id.lang
        lang = self.env['res.lang'].search([('code', '=', user_lang_str)])
        lang_format = lang.date_format

        report_name =\
            'hr_timesheet_details_report.hr_timesheet_details_report'
        report = report_obj._get_report_from_name(report_name)
        projects = project_obj.browse(data['project_ids'])
        account_ids = [project.analytic_account_id.id for project in projects]

        domain = [('user_id', '=', data['user_id'][0]),
                  ('date', '>=', data['period_start']),
                  ('date', '<=', data['period_end'])]
        if account_ids:
            domain.append(('account_id', 'in', account_ids))

        timesheet_lines = hr_analytic_timesheet.search(domain)

        timesheet_by_dates = {}
        hours_total = 0
        for l in timesheet_lines:
            date = datetime.strptime(l.date, DEFAULT_SERVER_DATE_FORMAT)
            if date not in timesheet_by_dates:
                timesheet_by_dates[date] = []
            timesheet_by_dates[date].append(l)
            hours_total += l.unit_amount

        # build the list of all days between period_start and period_end
        days = []

        start = datetime.strptime(data['period_start'],
                                  DEFAULT_SERVER_DATE_FORMAT)
        end = datetime.strptime(data['period_end'], DEFAULT_SERVER_DATE_FORMAT)

        for single_date in\
                list(dateutil.rrule.rrule(dateutil.rrule.DAILY, dtstart=start,
                                          until=end)):
            if single_date not in timesheet_by_dates:
                timesheet_by_dates[single_date] = [False]
            days.append(single_date)
        wiz = self.env['hr.timesheet.details.report.wizard'].browse([data['id']])
        wiz.total_hours = hours_total
        hours_total = round(hours_total, 3)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'user_name': user_name,
            'period_start': start,
            'period_end': end,
            'timesheet_by_dates': timesheet_by_dates,
            'days': days,
            'lang_format': lang_format,
            'filter_customer': data.get('filter_customer', False),
            'total_hours': hours_total,
        }

        return report_obj.render(
            'hr_timesheet_details_report.hr_timesheet_details_report',
            docargs)
