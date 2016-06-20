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


class WorkflowWorkitem(models.Model):
    _inherit = 'workflow.workitem'

    task_ids = fields.One2many(comodel_name='workflow.task',
                               inverse_name='workitem', string='Tasks')

    @api.multi
    def execute_delete(self):
        for record in self:
            record.task_ids.close_task()
            record.task_ids.write({'workitem': False})
        return super(WorkflowWorkitem, self).execute_delete()
