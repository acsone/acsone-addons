# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields

PROJECT_SELECTION = [('template', 'Template'),
                     ('draft', 'New'),
                     ('open', 'In Progress'),
                     ('cancelled', 'Cancelled'),
                     ('pending', 'Pending'),
                     ('close', 'Closed')]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_closed = fields.Boolean(related='stage_id.closed', string='Closed')
    project_state = fields.Selection(PROJECT_SELECTION,
                                     related='project_id.state',
                                     string='Project State')
