# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of workflow_task,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     workflow_task is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     workflow_task is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with workflow_task.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class Task(models.Model):
    _name = 'workflow.task'
    _inherit = ['mail.thread']

    @api.model
    def _select_objects(self):
        model_obj = self.env['ir.model']
        models = model_obj.search([])
        return [(r.model, r.name) for r in models] + [('', '')]

    workitem = fields.Many2one(comodel_name='workflow.workitem')
    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity', required=True)
    description = fields.Text()
    user_id = fields.Many2one(comodel_name='res.users', string='Assign User',
                              track_visibility='onchange')
    state = fields.Selection([('new', 'Todo'),
                              ('running', 'In progress'),
                              ('closed', 'Closed')], default='new',
                             track_visibility='onchange')
    date_done = fields.Datetime(track_visibility='onchange')
    res_type = fields.Selection(selection=_select_objects, string='Type',
                                required=True)
    res_id = fields.Integer(string='ID', required=True)
    ref_object = fields.Reference(string='Reference record',
                                  selection=_select_objects,
                                  store=True, compute='_get_ref_object')
    action_ids = fields.One2many(related='activity_id.action_ids')

    @api.multi
    def start_task(self):
        self.ensure_one()
        if self.state == 'new':
            self.state = 'running'

    @api.multi
    def close_task(self):
        self.ensure_one()
        if self.state == 'running':
            self.date_done = fields.Datetime.now()
            self.state = 'closed'

    @api.depends('res_type', 'res_id')
    @api.one
    def _get_ref_object(self):
        if self.res_type and self.res_id:
            self.ref_object = '%s,%s' % (self.res_type, str(self.res_id))
