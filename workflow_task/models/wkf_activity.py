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


class WorkflowActivityAction(models.Model):
    _name = 'workflow.activity.action'

    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity')
    name = fields.Char(required=True)
    action = fields.Many2one(comodel_name='ir.actions.server', required=True)

    @api.multi
    def do_action(self):
        self.ensure_one()
        res_id = self.env.context.get('res_id', False)
        res_type = self.env.context.get('res_type', False)
        assert res_id and res_type
        ctx = dict(self.env.context,
                   active_model=res_type, active_ids=[res_id],
                   active_id=res_id)
        self.action.with_context(ctx).run()


class WorkflowActivity(models.Model):
    _inherit = 'workflow.activity'

    task_create = fields.Boolean()
    task_description = fields.Text()
    action_ids = fields.One2many(comodel_name='workflow.activity.action',
                                 inverse_name='activity_id', string='Action')

    @api.multi
    def _execute(self, workitem_id):
        self.ensure_one()
        res = super(WorkflowActivity, self)._execute(workitem_id)
        if self.task_create:
            self.create_task(workitem_id)
        return res

    @api.multi
    def _prepare_task_vals(self, workitem_id):
        self.ensure_one()
        workitem = self.env['workflow.workitem'].browse([workitem_id])
        res_type = workitem.inst_id.res_type
        res_id = workitem.inst_id.res_id
        return {
            'res_type': res_type,
            'res_id': res_id,
            'description': self.task_description,
            'workitem': workitem_id,
            'activity_id': self.id,
        }

    @api.multi
    def create_task(self, workitem_id):
        self.ensure_one()
        task_obj = self.env['workflow.task']
        vals = self._prepare_task_vals(workitem_id)
        task_obj.create(vals)
