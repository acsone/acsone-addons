# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of project_code, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     project_code is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     project_code is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with project_code.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestProjectCode(common.TransactionCase):

    def test_0_sanity(self):
        p = self.env.ref('project.all_projects_account')
        self.assertEqual(p.name, "Projects", "Unexpected demo data")
        self.assertEqual(p.code, "PP001", "Unexpected demo data")

    def test_1_display_name(self):
        p = self.env.ref('project.all_projects_account')
        self.assertEqual(p.display_name, "PP001 - Projects")

    def test_2_complete_name(self):
        p = self.env.ref('project.all_projects_account')
        self.assertEqual(p.complete_name, "PP001 - Projects")
