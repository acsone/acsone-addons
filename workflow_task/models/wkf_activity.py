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
import time

from openerp import models, fields, api, exceptions, _
from openerp.osv import expression
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import SUPERUSER_ID


class WorkflowActivityAction(models.Model):
    _name = 'workflow.activity.action'

    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity',
                                  required=True)
    name = fields.Char(required=True)
    action = fields.Many2one(comodel_name='ir.actions.server', required=True)

    @api.multi
    def do_action(self):
        self.ensure_one()
        res_id = self.env.context.get('res_id', False)
        res_type = self.env.context.get('res_type', False)
        assert res_id and res_type
        self.activity_id.check_action_security(res_type, res_id)
        self = self.suspend_security()
        ctx = dict(self.env.context,
                   active_model=res_type, active_ids=[res_id],
                   active_id=res_id)
        res = self.action.with_context(ctx).run()
        return res


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
    use_action_object = fields.Boolean(string="Use actions on object")
    use_action_task = fields.Boolean(string="Use actions on task")
    action_domain = fields.Char()
    action_group = fields.Many2one(comodel_name='res.groups')
    condition = fields.Selection(selection=[('or', 'OR'), ('and', 'AND')],
                                 default='and', required=True)
    # TODO: rename task_action_ids
    action_ids = fields.One2many(comodel_name='workflow.activity.action',
                                 inverse_name='activity_id',
                                 string='Actions',
                                 help="Actions that can be triggered with "
                                      "buttons on the task form. This is "
                                      "useful when the activity cannot be "
                                      "completed through normal actions "
                                      "on the underlying object.")

    @api.model
    def _eval_context(self):
        return {'user': self.env.user,
                'time': time}

    @api.multi
    def check_action_security(self, res_type, res_id):
        if not self._check_action_security(res_type, res_id):
            raise exceptions.AccessError(
                _("""The requested operation cannot be completed due to
                     security restrictions.
                     Please contact your system administrator."""))

    @api.multi
    def _check_action_security(self, res_type, res_id):
        self.ensure_one()
        if self.env.user.id == SUPERUSER_ID:
            return True
        check_group = False
        check_domain = False
        if self.action_group.id and\
                (self.action_group.id in self.env.user.groups_id.ids):
            check_group = True
        if not self.action_group.id:
            check_group = True
        eval_context = self._eval_context()
        if self.action_domain:
            domain = expression.normalize_domain(eval(self.action_domain,
                                                      eval_context))
            if res_id in self.env[res_type].search(domain).ids:
                check_domain = True
        else:
            check_domain = True
        str_condition = ("%s %s %s") % (check_domain, self.condition,
                                        check_group)
        if eval(str_condition):
            return True
        else:
            return False

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
        if self.task_deadline_days:
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
            vals['date_critical'] = fields.Date.context_today(self, date_critical)
            vals['date_deadline'] = fields.Date.context_today(self, date_deadline)
        return vals

    @api.multi
    def create_task(self, workitem_id):
        self.ensure_one()
        task_obj = self.env['workflow.task']
        vals = self._prepare_task_vals(workitem_id)
        task_obj.create(vals)
