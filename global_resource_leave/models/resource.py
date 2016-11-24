# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of global_resource_leave,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     global_resource_leave is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     global_resource_leave is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with global_resource_leave.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    calendar_leave_ids = fields.One2many(
        comodel_name='resource.calendar.leaves', inverse_name='calendar_id',
        string='Calendar Leaves')

    leave_ids = fields.Many2many(comodel_name='resource.calendar.leaves',
                                 string='All Leaves',
                                 compute='_compute_all_leaves')

    @api.one
    @api.depends('calendar_leave_ids')
    def _compute_all_leaves(self):
        global_leaves = self.env['resource.calendar.leaves'].search(
            [('calendar_id', '=', False),
             ('resource_id', '=', False),
             '|',
             ('company_id', '=', self.company_id.id),
             ('company_id', '=', False)])
        all_leaves = global_leaves + self.calendar_leave_ids
        self.leave_ids = all_leaves


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.one
    @api.depends('calendar_id', 'calendar_id.company_id', 'force_company_id')
    def _compute_company_id(self):
        if self.calendar_id:
            self.company_id = self.calendar_id.company_id
        else:
            self.company_id = self.force_company_id

    company_id = fields.Many2one(comodel_name='res.company', string="Company",
                                 store=True, compute='_compute_company_id')
    force_company_id = fields.Many2one(comodel_name='res.company',
                                       string="Company")
