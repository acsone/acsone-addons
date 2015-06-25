# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of project_member_ext,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     project_member_ext is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     project_member_ext is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with project_member_ext.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class project_project(models.Model):
    _inherit = 'project.project'

    @api.one
    def get_children_projects(self):
        """ Return the list of children projects
        A project is a subproject of one other if the linked 'Analytic Account'
        is child of an other 'Analytic Account' linked to a project.
        """
        self.env.cr.execute("""
            SELECT project.id
            FROM project_project project, project_project parent,
            account_analytic_account account
            WHERE project.analytic_account_id = account.id
            AND parent.analytic_account_id = account.parent_id
            AND parent.id = %s
        """, (self.id,))
        sub_project_ids = self.env.cr.fetchall()
        return self.search([('id', 'in', sub_project_ids)])

    @api.one
    def apply_members_changes(self, changes):
        current_member_ids = self.members.ids
        new_changes = []
        for change in changes:
            act, the_id = change[:2]
            if (act not in (0, 2) or
                (act == 6) or
                (act in (3, 5) and the_id in current_member_ids) or
                    (act in (4,) and the_id not in current_member_ids)):
                new_changes.append(change)
        if new_changes:
            self.write({'members': new_changes})

    @api.multi
    def write(self, vals):
        res = super(project_project, self).write(vals)
        if 'members' in vals:
            for subproject in self.get_children_projects():
                subproject.apply_members_changes(vals['members'])
        return res
