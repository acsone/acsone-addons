# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    calendar_leave_ids = fields.One2many(
        comodel_name='resource.calendar.leaves', inverse_name='calendar_id',
        string='Calendar Leaves')

    leave_ids = fields.Many2many(comodel_name='resource.calendar.leaves',
                                 string='All Leaves',
                                 compute='_compute_all_leaves')

    @api.multi
    @api.depends('calendar_leave_ids')
    def _compute_all_leaves(self):
        for record in self:
            global_leaves = self.env['resource.calendar.leaves'].search(
                [('calendar_id', '=', False),
                 ('resource_id', '=', False),
                 '|',
                 ('company_id', '=', record.company_id.id),
                 ('company_id', '=', False)])
            all_leaves = global_leaves + record.calendar_leave_ids
            record.leave_ids = all_leaves


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.multi
    @api.depends('calendar_id', 'calendar_id.company_id', 'force_company_id')
    def _compute_company_id(self):
        for record in self:
            if record.calendar_id:
                record.company_id = record.calendar_id.company_id
            else:
                record.company_id = record.force_company_id

    company_id = fields.Many2one(comodel_name='res.company', string="Company",
                                 store=True, compute='_compute_company_id')
    force_company_id = fields.Many2one(comodel_name='res.company',
                                       string="Company")
