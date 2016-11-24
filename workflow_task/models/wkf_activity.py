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

import datetime

from openerp import models, fields, api


class WorkflowActivity(models.Model):
    _inherit = 'workflow.activity'

    res_type = fields.Char(related='wkf_id.osv', store=True,
                           readonly=True)
    task_create = fields.Boolean(string='Create Task',
                                 help="If checked, the workflow engine will "
                                      "create a task when entering this "
                                      "activity and close the task "
                                      "when exiting the activity.")
    task_description = fields.Text(help="A text to explain the user what "
                                        "he needs to do to accomplish the "
                                        "task.")
    task_deadline_days = fields.Integer(string='Deadline days')
    deadline_start_date = fields.Many2one(
        comodel_name='ir.model.fields', string="Compute deadline from",
        help="""If empty, deadline will be computed
                from the task creation date""")
    critical_delay = fields.Integer(
        string="Critical delay (days)",
        help="""The created task will appear in red in the task tree view
            in the number of days before the deadline.""")
    use_action_task = fields.Boolean(string="Show actions on task")

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
        obj = self.env[res_type].browse([res_id])
        vals = {
            'res_type': res_type,
            'res_id': res_id,
            'description': self.task_description,
            'workitem': workitem_id,
            'activity_id': self.id,
        }
        if self.deadline_start_date:
            start_date = False
            if self.deadline_start_date.id:
                date = getattr(obj, self.deadline_start_date.name)
                if date:
                    start_date = fields.Date.from_string(date)
            if not start_date:
                start_date = datetime.date.today()
            date_deadline = start_date + \
                datetime.timedelta(days=self.task_deadline_days)
            if self.critical_delay:
                date_critical = date_deadline - \
                    datetime.timedelta(days=self.critical_delay)
            else:
                date_critical = date_deadline
            vals['date_critical'] = fields.Date.context_today(self,
                                                              date_critical)
            vals['date_deadline'] = fields.Date.context_today(self,
                                                              date_deadline)
        return vals

    @api.multi
    def create_task(self, workitem_id):
        self.ensure_one()
        task_obj = self.env['workflow.task']
        vals = self._prepare_task_vals(workitem_id)
        ctx = self.env.context.copy()
        ctx['tracking_disable'] = True
        task_obj.suspend_security().with_context(ctx).create(vals)
