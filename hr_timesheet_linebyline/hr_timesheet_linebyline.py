# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Olivier Laurent & Stéphane Bidoul
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
##############################################################################

from osv import fields, osv
import datetime

class hr_timesheet_sheet(osv.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    # make timesheet_ids a normal one2many relation, so it shows
    # all timesheet lines and not only the lines of date_current
    _columns = {
        'timesheet_ids' : fields.one2many('hr.analytic.timesheet', 'sheet_id',
            'Timesheet lines',
            readonly=True, states={
                'draft': [('readonly', False)],
                'new': [('readonly', False)]}
            ),
    }
    
    _order = "date_from desc"

    def convert_dates(self, date_current, date_from, date_to):
        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        current_dt = datetime.datetime.strptime(date_current, DATETIME_FORMAT)
        return (current_dt, from_dt, to_dt)

    def get_next_sunday_or_end_of_month(self, dt):
        ndt = dt + datetime.timedelta(days=6-dt.weekday())
        if ndt.month != dt.month:
            ndt = datetime.datetime(ndt.year,ndt.month,1) - datetime.timedelta(days=1)
        return ndt

    def on_change_date_period_from(self, cr, uid, ids, date_current, date_from, date_to, context=None):
        current_dt, from_dt, to_dt = self.convert_dates(date_current, date_from, date_to)
        # propose a new to date
        to_dt = self.get_next_sunday_or_end_of_month(from_dt)
        # make sure current_dt is in the period
        if current_dt < from_dt or current_dt > to_dt:
            current_dt = from_dt
        return {'value': {'date_current': current_dt.isoformat()[:10],
                          'date_from': from_dt.isoformat()[:10],
                          'date_to': to_dt.isoformat()[:10]} }

    def write(self, cr, uid, ids, vals, context=None):
        """
        Make sure the to_invoice flag is set on timesheet lines only when
        the timesheet is approved, and is not set otherwise.
        """
        tsl_obj = self.pool.get('hr.analytic.timesheet')
        account_obj = self.pool.get('account.analytic.account')
        line_obj = self.pool.get('account.analytic.line')
        for ts in self.browse(cr, uid, ids, context=context):
            state = vals.get('state',ts.state)
            tsl_ids = tsl_obj.search(cr, uid, [('sheet_id','=',ts.id)], context=context)
            for tsl in tsl_obj.browse(cr, uid, tsl_ids, context=context):
                if state == 'done' and tsl.account_id and not tsl.invoice_id:
                    account = account_obj.browse(cr, uid, [tsl.account_id.id])[0]
                    to_invoice = account.to_invoice.id
                else:
                    # not invoiced, set to_invoice to False, else leave it alone
                    if not tsl.invoice_id:
                        to_invoice = False
                    else:
                        to_invoice = tsl.to_invoice
                if (tsl.to_invoice or False) != to_invoice:
                    # we go through the account analytic line because we cannot change
                    # a timesheet that is not draft or new
                    line = line_obj.browse(cr, uid, [tsl.line_id.id])[0]
                    line_obj.write(cr, uid, [line.id], {'to_invoice': to_invoice}, context=context)
        return super(hr_timesheet_sheet, self).write(cr, uid, ids, vals, context=context)

class hr_analytic_timesheet(osv.Model):
    _inherit = "hr.analytic.timesheet"

    def _get_default_account_id(self, cr, uid, context=None):
        if context.get('user_id'):
            user = self.pool.get("res.users").browse(cr,uid,[context['user_id']],context=context)[0]
            if user.context_project_id:
                return user.context_project_id.analytic_account_id.id
        return False

    def on_change_account_id(self, cr, uid, ids, account_id, context=None):
        to_invoice = False
        task_id = False
        if account_id:
            project_obj = self.pool.get("project.project")
            project_ids = project_obj.search(cr, uid, [('analytic_account_id','=',account_id)])
            if project_ids:
                assert len(project_ids) == 1
                project = project_obj.browse(cr, uid, project_ids[0], context)
                to_invoice = project.to_invoice.id
                if len([task for task in project.tasks if task.state == 'open']) == 1:
                    task_id = project.tasks[0].id
        return {'value': {'task_id': task_id, 'to_invoice': to_invoice}}

    def on_change_date(self, cr, uid, ids, date, context=None):
        """ Coerce date within timesheet period """
        if context is None:
            context = {}
        date_from = context.get('date_from')
        date_to = context.get('date_to')
        if date and date_from and date_to:
            if date < date_from:
                date = date_from
            if date > date_to:
                date = date_to
        return {'value': {'date': date}}

    def create(self, cr, uid, vals, context=None):
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        sheet_ids = sheet_obj.search(cr, uid, [('user_id','=',vals['user_id']),('date_from','<=',vals['date']),('date_to','>=',vals['date'])])
        if sheet_ids:
            assert len(sheet_ids) == 1
            vals['sheet_id'] = sheet_ids[0]
        return super(hr_analytic_timesheet, self).create(cr, uid, vals, context=context)

    _defaults = {
        'account_id': _get_default_account_id,
        'date': False, # XXX we could propose a default date
    }

    """
    TODO: - (write or create) when saving a timesheet line for the first time, it should be necessary to force its to_invoice
            to False because it has inconditionnaly inherited the to_invoice value of its parent project
          - (on_change_account_id) while the sheet is not approved, il should be necessary to leave the to_invoice to False
    """

class account_analytic_line(osv.Model):
    _inherit = 'account.analytic.line'

    def _check_task_project(self, cr, uid, ids):
        project_obj = self.pool.get('project.project')
        for line in self.browse(cr, uid, ids):
            if line.task_id and line.account_id:
                if line.task_id.project_id.analytic_account_id.id != line.account_id.id:
                    return False
        return True

    _constraints = [
        (_check_task_project, 'Error! Task must belong to the project.', ['task_id','account_id']),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

