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

import openerp.tests.common as common


class TestProjectMembers(common.TransactionCase):

    def setUp(self):
        super(TestProjectMembers, self).setUp()
        self.project_1 = self.env.ref("project.project_project_1")
        # creaate an other project an define
        self.project_1_1 = self.env['project.project'].create({
            'name': 'Project 11',
            'code': 'PP001.1',
            'type': 'view'
        })
        # define the project as subproject of project_1
        parent_acc = self.project_1.analytic_account_id
        self.project_1_1.analytic_account_id.parent_id = parent_acc

        # and a third level subproject
        self.project_1_1_1 = self.env['project.project'].create({
            'name': 'Project 1.1.1',
            'code': 'PP001.1.1',
            'type': 'view'
        })
        # define the project as subproject of project_1
        parent_acc = self.project_1_1.analytic_account_id
        self.project_1_1_1.analytic_account_id.parent_id = parent_acc

    def test_get_children_projects(self):
        """The method should return direct children
        """
        children = self.project_1.get_children_projects()
        self.assertEqual(1, len(children))
        self.assertEqual([self.project_1_1], children)

        children = self.project_1_1_1.get_children_projects()
        self.assertEqual(1, len(children))

    def test_members_add(self):
        admin = self.env.ref('base.user_root')
        demo = self.env.ref('base.user_demo')
        self.assertEqual(0, len(self.project_1_1.members))
        self.project_1_1.write({'members': [(4, admin.id)]})
        self.assertEqual([admin.id], self.project_1_1.members.ids)
        self.assertEqual([admin.id], self.project_1_1_1.members.ids)

        # by default demo user is member of project_id. Iy's possible to
        # remove it without error even if it not exists in subproject
        self.assertTrue(demo in self.project_1.members)
        self.project_1.write({'members': [(3, demo.id)]})
        self.assertFalse(demo in self.project_1.members)

        # set a list of ids at root
        self.project_1.write({'members': [(6, None, [demo.id, admin.id])]})
        self.assertTrue(demo in self.project_1_1_1.members)
        self.assertTrue(admin in self.project_1_1_1.members)

        # unlink all at level project_1
        self.project_1.write({'members': [(5, None)]})
        self.assertEqual(0, len(self.project_1_1.members))
        self.assertEqual(0, len(self.project_1_1_1.members))

        # create and assign a user in this case, the new user will not
        # be added recursively it's a limitation
        self.project_1.write({'members': [(0, 0, {
            'name': 'acsone_user',
            'company_id': self.env.ref('base.main_company').id,
            'customer': False,
            'email': 'acsone@test.eu',
            'login': 'acsone_user',
            'password': 'acsone_pwd',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('base.group_partner_manager').id])]
            })]})
        self.assertEqual(1, len(self.project_1.members))
        self.assertEqual(0, len(self.project_1_1.members))
        new_user = self.project_1.members[0]

        # add the user to all levels
        self.project_1_1.write({'members': [(4, new_user.id)]})
        self.assertEqual(1, len(self.project_1.members))
        self.assertEqual(1, len(self.project_1_1.members))
        self.assertEqual(1, len(self.project_1_1_1.members))

        # unlink: that will also delete the relationship on subuprojects
        # because of the ondelete
        self.project_1.write({'members': [(2, new_user.id)]})
        self.assertEqual(0, len(self.project_1.members))
        self.assertEqual(0, len(self.project_1_1.members))
        self.assertEqual(0, len(self.project_1_1_1.members))
