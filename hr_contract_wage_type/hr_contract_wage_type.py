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

from openerp import models, fields, api
from openerp.osv import orm


class hr_contract_wage_type_period(models.Model):

    """ Contract Wage Type Period """
    _name = 'hr.contract.wage.type.period'
    _description = 'Wage Period'

    name = fields.Char('Period Name', size=50, required=True, select=True)
    factor_days = fields.Float('Hours in the Period', digits=(12, 4),
                               required=True, default=168.0)


class hr_contract_wage_type(models.Model):

    """ Contract Wage Type (hourly, daily, monthly, ...) """
    _name = 'hr.contract.wage.type'
    _description = 'Wage Type'

    name = fields.Char('Wage Type Name', size=50, required=True, select=True)
    period_id = fields.Many2one('hr.contract.wage.type.period',
                                'Wage Period', required=True)
    type = fields.Selection([('gross', 'Gross'), ('net', 'Net')],
                            'Type', required=True, default='gross')
    factor_type = fields.Float(
        'Factor for Hour Cost', digits=(12, 4), required=True, default=1.8,
        help='This field is used by the timesheet system to compute '
        'the cost of an hour of work based on the contract of the employee')


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    def _get_hourly_wage(self, cwt, wage):
        p = cwt.period_id
        if p:
            # Prevent divison-by-zero error
            if p.factor_days:
                return wage * cwt.factor_type / p.factor_days
            else:
                return 0.0
        else:
            return 0.0

    @api.multi
    def _hourly_wage(self):
        for contract in self:
            contract.hourly_wage = False
            cwt = contract.wage_type_id
            if cwt:
                contract.hourly_wage = self._get_hourly_wage(cwt,
                                                             contract.wage)

    wage_type_id = fields.Many2one('hr.contract.wage.type',
                                   'Wage Type', required=True)
    hourly_wage = fields.Float(string='Hourly wage', compute='_hourly_wage',
                               digits=(16, 20))


class hr_employee(orm.Model):
    _inherit = "hr.employee"

    def get_hourly_wage_on_date(self, cr, uid, ids, date, context=None):
        """ Return the hourly wage of employees from the contracts,
            or False if no contract is defined at requested date

            :param ids: employee ids
            :param date: validity date of the contract
        """
        res = {}
        for employees in self.browse(cr, uid, ids, context=context):
            num = False
            if employees.contract_ids:
                for contract in employees.contract_ids:
                    if contract.date_start <= date:
                        if not contract.date_end or contract.date_end >= date:
                            num = contract.hourly_wage
            res[employees.id] = num
        return res
