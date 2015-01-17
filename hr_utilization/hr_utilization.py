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

from openerp import models, fields, api

from openerp.tools.translate import _


class res_company(models.Model):
    _inherit = "res.company"

    fulltime_calendar_id = fields.Many2one(
        "resource.calendar", "Full-time Calendar", required=False,
        help="Calendar used as the full working time reference"
        " of the company.")


class resource_calendar(models.Model):
    _inherit = "resource.calendar"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for cal in self.browse(cr, uid, ids, context=context):
            if cal.company_id:
                name = "%s (%s)" % (cal.name, cal.company_id.name)
            else:
                name = cal.name
            res.append((cal.id, name))
        return res

    leave_ids = fields.One2many('resource.calendar.leaves', 'calendar_id',
                                'Closing Days')


class hr_utilization_configuration(models.Model):
    _name = 'hr.utilization.configuration'

    def _get_column_list(self, configuration_column_ids):
        ''' Build a list of columns '''
        result = []
        for configuration_column_id in configuration_column_ids:
            result.append(configuration_column_id.column_id.short_name)
        return ", ".join(result) or False

    @api.one
    @api.depends('configuration_column_ids')
    def _column_list(self):
        ''' Build a set of columns lists '''
        self.column_list = self._get_column_list(self.configuration_column_ids)

    def copy(self, cr, uid, id, defaults, context=None):
        previous_name = self.browse(cr, uid, id, context=context).name
        copy_name = _('Copy of %s') % previous_name
        new_name = copy_name
        n = 0
        while True:
            existing_ids = self.search(
                cr, uid, [('name', '=', new_name)], context=context)
            if not existing_ids:
                break
            n += 1
            new_name = '%s (%s)' % (copy_name, n)
        defaults['name'] = new_name
        return super(hr_utilization_configuration, self).copy(
            cr, uid, id, defaults, context=context)

    name = fields.Char('Utilization Configuration Name', size=128,
                       required=True)
    with_fte = fields.Boolean('With Full-time Equivalent Column',
                              required=True, default=True)
    configuration_column_ids = fields.One2many(
        'hr.utilization.configuration.column',
        'configuration_id',
        'List of Columns to Print')
    column_list = fields.Char(compute='_column_list', string='Columns')

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Configuration name must be unique'),
    ]
    _order = "name"


class hr_utilization_configuration_column(models.Model):
    _name = 'hr.utilization.configuration.column'
    _rec_name = 'column_id'

    column_id = fields.Many2one('hr.utilization.column', 'Column',
                                required=True, ondelete='cascade')
    configuration_id = fields.Many2one('hr.utilization.configuration',
                                       'Configuration', required=True,
                                       ondelete='cascade')
    sequence = fields.Integer('Sequence', required=True)

    _order = "sequence"


class hr_utilization_column(models.Model):
    _name = 'hr.utilization.column'

    def _get_analytic_account_list(self, analytic_accounts):
        ''' Build a list of analytic accounts codes '''
        return ", ".join([r.display_name for r in analytic_accounts])

    @api.one
    @api.depends('analytic_account_ids')
    def _analytic_account_list(self):
        ''' Build a set of analytic accounts codes lists '''
        self.analytic_account_list = self._get_analytic_account_list(
            self.analytic_account_ids)

    def copy(self, cr, uid, id, defaults, context=None):
        source = self.browse(cr, uid, id, context=context)
        previous_name = source.name
        previous_short_name = source.short_name
        copy_name = _('Copy of %s') % previous_name
        new_name = copy_name
        n = 0
        while True:
            new_short_name = '%s-%s' % (n, previous_short_name)
            existing_ids = self.search(
                cr, uid, ['|',
                          ('name', '=', new_name),
                          ('short_name', '=', new_short_name)],
                context=context)
            if not existing_ids:
                break
            n += 1
            new_name = '%s (%s)' % (copy_name, n)
        defaults['name'] = new_name
        defaults['short_name'] = new_short_name
        return super(hr_utilization_column, self).copy(
            cr, uid, id, defaults, context=context)

    name = fields.Char('Column Name', size=128, required=True)
    short_name = fields.Char('Report Column Name', size=15, required=True)
    analytic_account_ids = fields.Many2many('account.analytic.account',
                                            string='Analytic accounts')
    analytic_account_list = fields.Char(compute='_analytic_account_list',
                                        string='Analytic accounts')

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Column name must be unique'),
        ('unique_name', 'unique(short_name)',
         'Column short name must be unique'),
    ]
    _order = "name"
