# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of workflow_activity_action,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     workflow_activity_action is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     workflow_activity_action is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with workflow_activity_action.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class WorkflowActionModel(models.AbstractModel):
    _name = 'workflow.action.model'

    activity_action_ids = fields.One2many(
        comodel_name='workflow.activity.action',
        compute='_get_action_ids', string="Action")

    @api.multi
    def _get_action_ids(self):
        res_type = str(self._model)
        for record in self:
            if record.id:
                workitem_ids = self.env['workflow.workitem']\
                    .search([('inst_id.res_id', '=', record.id),
                             ('inst_id.res_type', '=', res_type)])
                actions_ids = self.env['workflow.activity.action']
                activity_ids = workitem_ids.mapped('act_id')
                for activity in activity_ids:
                    if activity.use_action_object and\
                            activity._check_action_security(res_type,
                                                            record.id):
                        actions_ids = actions_ids + activity.action_ids
                self.activity_action_ids = actions_ids
