# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of analytic_code, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     analytic_code is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     analytic_code is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with analytic_code.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class test_analytic_code(common.TransactionCase):

    def setUp(self):
        super(test_analytic_code, self).setUp()
        self.al = self.env["account.analytic.account"].browse(
            self.ref('account.analytic_seagate_p1'))
        self.al.code = 'AA042'

    def test_0_sanity(self):
        self.assertEqual(self.al.name, "Seagate P1", "Unexpected demo data")
        self.assertEqual(self.al.code, "AA042", "Unexpected demo data")

    def test_1_complete_name(self):
        self.assertEqual(self.al.complete_name, "AA042 - Seagate P1")
