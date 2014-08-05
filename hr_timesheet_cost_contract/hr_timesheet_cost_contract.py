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

from openerp import SUPERUSER_ID
from openerp.osv import osv

from openerp.tools.translate import _


class hr_timesheet_sheet(osv.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    def update_timesheets_cost_from_contract(self, cr, uid, ids, context=None):
        ts_obj = self.pool.get('hr.analytic.timesheet')
        for sheet in self.browse(cr, uid, ids, context=context):
            ts_ids = ts_obj.search(
                cr, uid, [('sheet_id', '=', sheet.id)], context=context)
            ts_obj.update_cost_from_contract(
                cr, uid, ts_ids, sheet.employee_id.id, context=context)

    def button_confirm(self, cr, uid, ids, context=None):
        self.update_timesheets_cost_from_contract(
            cr, SUPERUSER_ID, ids, context=context)
        return super(hr_timesheet_sheet, self).button_confirm(
            cr, uid, ids, context=context)


class hr_analytic_timesheet(osv.Model):
    _inherit = "hr.analytic.timesheet"

    def update_cost_from_contract(self, cr, uid, ids, employee_id,
                                  context=None):
        employee_obj = self.pool.get('hr.employee')
        for ts in self.browse(cr, uid, ids, context=context):
            hourly_wage = employee_obj.get_hourly_wage_on_date(
                cr, uid, [employee_id], ts.date, context=context)[employee_id]
            if hourly_wage is False:
                employee = employee_obj.browse(
                    cr, uid, [employee_id], context=context)[0]
                raise osv.except_osv(
                    _('Error !'),
                    _('No contract defined for employee %s '
                      'on timesheet date %s') % (employee.name, ts.date))
            self.write(
                cr, uid, [ts.id], {'amount': -hourly_wage * ts.unit_amount})
