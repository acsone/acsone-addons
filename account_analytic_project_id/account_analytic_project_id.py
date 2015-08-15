# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Stéphane Bidoul
#    Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
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

from openerp import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    project_id = fields.Many2one(
        'project.project', 'Project', copy=False,
        index=True)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        project = super(ProjectProject, self).create(vals)
        project.analytic_account_id.sudo().write({'project_id': project.id})
        return project
