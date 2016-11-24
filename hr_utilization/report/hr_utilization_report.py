# -*- coding: utf-8 -*-
#
#
# Authors: Stéphane Bidoul & Olivier Laurent
# Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#

import datetime
import time
import pytz
from dateutil import rrule, parser

from openerp.report import report_sxw

from openerp.addons.account_financial_report_webkit.report \
    import webkit_parser_header_fix

from openerp.osv import osv
from openerp.tools.translate import _


class hr_utilization_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(hr_utilization_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
        })

    def count_dayofweek(self, dayofweek, start, end, holidays):
        ''' Compute count of working dayofweek in a given period '''
        rs = rrule.rruleset()
        start = parser.parse(start)
        end = parser.parse(end)
        rs.rrule(
            rrule.rrule(rrule.DAILY, byweekday=dayofweek, dtstart=start,
                        until=end))
        for holiday in holidays:
            rs.exdate(datetime.datetime.combine(
                holiday, datetime.time(0, 0, 0)))
        return rs.count()

    def get_planned_working_hours(self, calendar_id, period_start,
                                  period_end):
        ''' Compute planned working time related to a period of a specific
            calendar
            Important: we use the administrator's timezone to convert leave
            datetimes to leave dates.
        '''
        # this method does more or less what we want but not quite...
        # return calendar_id._interval_hours_get(parser.parse(period_start),
        # parser.parse(period_end), timezone_from_uid=1)

        # unfortunately, leaves are datetimes not dates
        # and timesheets are entered for date not datetimes, so we must
        # reconcile the timezones somehow... here we assume the leaves
        # are entered in the timezone of the administrator
        localtz = None
        users_obj = self.pool.get('res.users')
        user_timezone = users_obj.browse(
            self.localcontext['cr'], self.localcontext['uid'], 1).tz
        if user_timezone:
            try:
                localtz = pytz.timezone(user_timezone)
            except pytz.UnknownTimeZoneError:
                pass
        if not localtz:
            raise osv.except_osv(_('Configuration Error!'), _(
                'Administrator user has no timezone defined; its timezone '
                'is necessary to process the leaves'))

        holidays = []
        for leave in calendar_id.leave_ids:
            dtf = datetime.datetime.strptime(
                leave.date_from, '%Y-%m-%d %H:%M:%S')
            dtt = datetime.datetime.strptime(
                leave.date_to, '%Y-%m-%d %H:%M:%S')
            no = dtt - dtf
            if no.days > 1 or (no.days == 1 and no.seconds > 0):
                raise osv.except_osv(_('Configuration Error!'), _(
                    'Leaves of more than one day not supported '
                    '(%s - %s)!' % (dtf, dtt)))
            holidays.append(localtz.fromutc(dtf).date())

        hours = 0.0
        for attendance in calendar_id.attendance_ids:
            attendance_hours = attendance.hour_to - attendance.hour_from
            hours += self.count_dayofweek(
                int(attendance.dayofweek),
                period_start, period_end, holidays) * attendance_hours
        return hours

    def get_total_planned_working_hours(self, period_start, period_end,
                                        contracts):
        ''' Compute total planned working time related to a period of a set
        of contracts '''
        hours = 0.0
        for contract in contracts:
            start = max(period_start, contract.date_start or period_start)
            end = min(period_end, contract.date_end or period_end)
            hours += self.get_planned_working_hours(
                contract.working_hours, start, end)
        return hours

    def set_context(self, objects, data, ids, report_type=None):
        ''' Build variables to print in the report '''

        # parameters
        OTHER = _("Other")
        TOTAL = _("Total")
        NA = _("N/A")

        # some initializations
        account_obj = self.pool.get("account.analytic.account")
        contract_obj = self.pool.get("hr.contract")

        # retrieve configuration to build column_names array
        configuration_obj = self.pool.get("hr.utilization.configuration")
        configuration = configuration_obj.browse(
            self.cr, self.uid, [data['configuration_id'][0]])[0]
        column_names = [
            configuration_column.column_id.short_name for
            configuration_column in configuration.configuration_column_ids]
        only_total = not len(column_names)
        if not only_total:
            column_names.append(OTHER)
        column_names.append(TOTAL)

        # populate a map of account id -> column name
        account_id_column_name_map = {}
        for configuration_column in configuration.configuration_column_ids:
            column = configuration_column.column_id
            for analytic_account_id in column.analytic_account_ids:
                # get all children
                account_ids = account_obj.search(
                    self.cr, self.uid,
                    [('parent_id', 'child_of', analytic_account_id.id),
                     ('type', '!=', 'view')])
                # populate map
                for account_id in account_ids:
                    assert account_id not in account_id_column_name_map
                    account_id_column_name_map[account_id] = column.short_name

        # get all contracts with a working schedule and group them by user
        contracts_with_schedule_by_id = {}
        contract_ids = contract_obj.search(self.cr, self.uid, [])
        contracts = contract_obj.browse(self.cr, self.uid, contract_ids)
        for contract in contracts:
            if contract.working_hours:
                contracts_with_schedule_by_id[contract.id] = contract

        # query hours grouped by account and employee
        # Note: this query assumes all timesheets are in an analytic journal
        # of type 'general'(which is the OpenErp default and the convention
        # used in account_analytic_analysis)
        # XXX: this query assumes all timesheets are entered in hours
        self.cr.execute("""
            select
                e.department_id,
                al.user_id,
                al.account_id,
                r.name,
                r.company_id,
                c.id,
                rc.fulltime_calendar_id,
                sum(al.unit_amount)
              from account_analytic_line al
              left join res_users u on u.id = al.user_id
              left join resource_resource r on r.user_id = u.id
              left join hr_employee e on e.resource_id = r.id
              left join hr_contract c on
                      c.employee_id = e.id and
                      (c.date_start is null or al.date >= c.date_start) and
                      (c.date_end is null or al.date <= c.date_end)
              left join res_company rc on rc.id = u.company_id
              where
                 al.journal_id = (select
                                    id
                                  from account_analytic_journal
                                  where type='general')
                and al.date >= %s and al.date <= %s
              group by e.department_id, al.user_id, al.account_id,
                       r.name, r.company_id, c.id, rc.fulltime_calendar_id
              order by r.name""", (data['period_start'], data['period_end']))

        # (user_id, has_schedule): {'name':name,'columns':{column_name:hours}}
        res = {}
        # (company_id, has_schedule):
        # {'name': name, 'users': [user_ids], 'departments': [departmen_ids],}
        res_company = {}
        # (department_id, has_schedule): {'name': name, 'users': [user_ids]}
        res_department = {}
        for department_id, user_id, account_id, user_name, company_id, \
                contract_id, fulltime_calendar_id, hours in self.cr.fetchall():
            has_schedule = contract_id in contracts_with_schedule_by_id

            if not data['group_by_company']:
                company_id = None
            if not data['group_by_department']:
                department_id = None

            user_key = (user_id, has_schedule)
            if user_key not in res:
                res[user_key] = {
                    'name': user_name,
                    'fulltime_calendar_id': fulltime_calendar_id,
                    'company_id': company_id,
                    'department_id': department_id,
                    'hours': {c_name: 0.0 for c_name in column_names},
                    'contracts': {},  # contract_id: contract
                }
            else:
                assert res[user_key]['company_id'] == company_id
                assert res[user_key]['department_id'] == department_id
            if only_total:
                column_name = TOTAL
            else:
                column_name = account_id_column_name_map.get(account_id, OTHER)
            if has_schedule:
                res[user_key]['contracts'][contract_id] = \
                    contracts_with_schedule_by_id[contract_id]

            res[user_key]['hours'][column_name] += hours

            company_key = (company_id, has_schedule)
            if company_key not in res_company:
                company_name = ''
                if company_id:
                    company_name = self.pool["res.company"].browse(
                        self.cr, self.uid, company_id).name
                res_company[company_key] = {
                    'name': company_name,
                    'users': [user_id],
                    'departments': [department_id],
                    'hours': {c_name: 0.0 for c_name in column_names}, }
            else:
                if user_id not in res_company[company_key]['users']:
                    res_company[company_key]['users'].\
                        append(user_id)
                if department_id not in \
                        res_company[company_key]['departments']:
                    res_company[company_key]['departments'].\
                        append(department_id)

            res_company[company_key]['hours'][column_name] += hours

            department_key = (department_id, company_id, has_schedule)
            if department_key not in res_department:
                department_name = ''
                if department_id:
                    department_name = self.pool["hr.department"].browse(
                        self.cr, self.uid, department_id).name
                res_department[department_key] = {
                    'name': department_name,
                    'company_id': company_id,
                    'users': [user_id],
                    'hours': {c_name: 0.0 for c_name in column_names}, }
            else:
                if user_id not in res_department[department_key]['users']:
                    res_department[department_key]['users'].\
                        append(user_id)

            res_department[department_key]['hours'][column_name] += hours

        # initialize totals
        users_without_contract = []
        with_fte = configuration.with_fte
        fte_with_na = False
        total_available_hours = 0.0

        res_total = {
            'name': TOTAL,
            'hours': {c_name: 0.0 for c_name in column_names},
        }
        if with_fte:
            res_total['fte'] = 0.0
        res_nc_total = {
            'name': TOTAL,
            'hours': {c_name: 0.0 for c_name in column_names},
        }

        # row total, percentages and fte for each row
        for (company_id, has_company_schedule), company in \
                res_company.items():
            company_available_hours = 0.0
            if with_fte:
                company['fte'] = 0.0
            if not only_total:
                company['hours'][TOTAL] = sum(company['hours'].values())
            for (department_id,
                 department_company_id,
                 has_department_schedule), department in \
                    res_department.items():
                if department_company_id == company_id and \
                        has_department_schedule == has_company_schedule:
                    department_available_hours = 0.0
                    if with_fte:
                        department['fte'] = 0.0
                    if not only_total:
                        department['hours'][TOTAL] = \
                            sum(department['hours'].values())
                    for (user_id, has_schedule), u in res.items():
                        if u['department_id'] == department_id and \
                                u['company_id'] == company_id and \
                                has_schedule == has_company_schedule and \
                                has_schedule == has_department_schedule:
                            # row total
                            if not only_total:
                                u['hours'][TOTAL] = sum(u['hours'].values())
                            if has_schedule:
                                # column totals
                                for column_name in column_names:
                                    res_total['hours'][column_name] += \
                                        u['hours'][column_name]
                                # percentage
                                available_hours = \
                                    self.get_total_planned_working_hours(
                                        data['period_start'],
                                        data['period_end'],
                                        u['contracts'].values())
                                total_available_hours += available_hours
                                company_available_hours += available_hours
                                department_available_hours += available_hours
                                u['pct'] = {}
                                for column_name, hours in u['hours'].items():
                                    u['pct'][column_name] = \
                                        hours / available_hours
                                # fte
                                if with_fte:
                                    if u['fulltime_calendar_id']:
                                        fulltime_calendar = \
                                            self.pool['resource.calendar'].\
                                            browse(self.cr, self.uid,
                                                   u['fulltime_calendar_id'])
                                        fte_available_hours = \
                                            self.get_planned_working_hours(
                                                fulltime_calendar,
                                                data['period_start'],
                                                data['period_end'])
                                        fte = available_hours / \
                                            fte_available_hours
                                        res_total['fte'] += fte
                                        company['fte'] += fte
                                        department['fte'] += fte
                                        u['fte'] = "%.1f" % fte
                                    else:
                                        u['fte'] = NA
                                        fte_with_na = True
                            else:
                                users_without_contract.append(u['name'])
                                # column totals
                                for column_name in column_names:
                                    res_nc_total['hours'][column_name] += \
                                        u['hours'][column_name]
                    if has_department_schedule:
                        department['pct'] = {
                            c_name: hours / department_available_hours
                            if department_available_hours else 0
                            for c_name, hours in department['hours'].items()}
                        if with_fte and fte_with_na and not department['fte']:
                            department['fte'] = NA
                        else:
                            department['fte'] = "%.1f" % department['fte']
            if has_company_schedule:
                company['pct'] = {
                    c_name: hours / company_available_hours
                    if company_available_hours else 0
                    for c_name, hours in company['hours'].items()}
                if with_fte and fte_with_na and not company['fte']:
                    company['fte'] = NA
                else:
                    company['fte'] = "%.1f" % company['fte']

        # total average percentage
        pct = res_total.setdefault('pct', {})
        for column_name, hours in res_total['hours'].items():
            if total_available_hours:
                pct[column_name] = hours / total_available_hours
            else:
                pct[column_name] = 0.0

        # total fte
        if with_fte and fte_with_na and not res_total['fte']:
            res_total['fte'] = NA
        else:
            res_total['fte'] = "%.1f" % res_total['fte']

        # set data in context for report
        data['res'] = res
        data['res_department'] = res_department
        data['res_company'] = res_company
        data['res_total'] = res_total
        data['res_nc_total'] = res_nc_total
        data['users_without_contract'] = users_without_contract
        data['column_names'] = column_names
        data['with_fte'] = with_fte
        data['fte_na'] = fte_with_na
        data['sort_criteria'] = column_names[0]

        # make report
        super(hr_utilization_report, self).set_context(
            objects, data, ids, report_type)


webkit_parser_header_fix.HeaderFooterTextWebKitParser(
    'report.hr.utilization.report',
    'hr.utilization.print',
    rml='addons/hr_utilization/report/hr_utilization_report.mako',
    parser=hr_utilization_report)
