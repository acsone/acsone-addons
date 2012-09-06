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

class hr_contract_wage_type_period(osv.Model):
    """ Contract wage type period name """
    _name = 'hr.contract.wage.type.period'
    _description = 'Wage Period'
    _columns = {
        'name': fields.char('Period Name', size=50, required=True, select=True),
        'factor_days': fields.float('Hours in the period', digits=(12,4), required=True, help='This field is used by the timesheet system to compute the price of an hour of work wased on the contract of the employee')
    }
    _defaults = {
        'factor_days': 168.0
    }

class hr_contract_wage_type(osv.Model):
    """ Contract wage type (hourly, daily, monthly, ...) """
    _name = 'hr.contract.wage.type'
    _description = 'Wage Type'
    _columns = {
        'name': fields.char('Wage Type Name', size=50, required=True, select=True),
        'period_id': fields.many2one('hr.contract.wage.type.period', 'Wage Period', required=True),
        'type': fields.selection([('gross','Gross'), ('net','Net')], 'Type', required=True),
        'factor_type': fields.float('Factor for hour cost', digits=(12,4), required=True, help='This field is used by the timesheet system to compute the price of an hour of work wased on the contract of the employee')
    }
    _defaults = {
        'type': 'gross',
        'factor_type': 1.8
    }

class hr_contract(osv.Model):
    _inherit = 'hr.contract'
    _columns = {
        'wage_type_id': fields.many2one('hr.contract.wage.type', 'Wage Type', required=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
