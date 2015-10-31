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

from openerp import models, fields


class Task(models.Model):
    _name = 'workflow.task'

    workitem = fields.Many2one(comodel_name='workflow.workitem')
    description = fields.Text()
    user_id = fields.Many2one(comodel_name='res.users')
    state = fields.Selection([('new', 'Todo'),
                              ('running', 'In progress'),
                              ('closed', 'Closed')])
    date_done = fields.Datetime()

    # view:
    # - bouton "start", visible dans l'état new
    # - les boutons définis sur l'activité, visibles dans l'état running
    # - lien vers la ressource concernée par le workflow instance
