# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of global_resource_leave,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     global_resource_leave is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     global_resource_leave is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with global_resource_leave.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common


class TestGlobalResourceLeave(common.TransactionCase):

    def setUp(self):
        super(TestGlobalResourceLeave, self).setUp()
        self.calendar01 = self.env.ref('resource.timesheet_group1')
        self.calendar_leave01 = \
            self.env.ref('resource.resource_analyst_leaves_demoleave1')
        self.global_leave01 = self.env.ref('resource.resource_dummyleave')
        company_obj = self.env['res.company']
        partner_obj = self.env['res.partner']
        partner = partner_obj.create(
            {"name": "Test",
             "is_company": True,
             "email": "test@tes.ttest",
             })
        self.company02 = company_obj.create(
            {"name": "Test",
             "partner_id": partner.id,
             "rml_header1": "My Company Tagline",
             "currency_id": self.ref("base.EUR")
             })

    def test_global_leave(self):
        # I ensure there isn't calendar on the leave
        self.assertFalse(self.global_leave01.calendar_id)
        # I check if the global leave is not in the leaves on the calendar
        self.assertFalse(self.global_leave01.id in
                         self.calendar01.leave_ids.ids)
        # I remove the resource on the leave
        self.global_leave01.resource_id = False
        self.calendar01.invalidate_cache()
        # I check if the global leave is in the leaves on the calendar
        self.assertTrue(self.global_leave01.id in
                        self.calendar01.leave_ids.ids)
        # I check if the leave on a calendar is correctly set
        self.assertTrue(
            self.calendar_leave01.calendar_id.id == self.calendar01.id)
        # I check if the calendar leave is in the leaves on the calendar
        self.assertTrue(self.calendar_leave01.id in
                        self.calendar01.leave_ids.ids)
        # I ensure the company on the global leave is the same than the
        # company on the calendar
        self.global_leave01.company_id = self.calendar01.company_id
        self.assertEqual(self.global_leave01.company_id.id,
                         self.calendar01.company_id.id)
        # I check if the global leave is in the leaves on the calendar
        self.assertTrue(self.global_leave01.id in
                        self.calendar01.leave_ids.ids)
        # I  change the company on the global leave
        self.global_leave01.company_id = self.company02
        # I check if the global leave isn't in the leaves on the calendar
        self.calendar01.leave_ids.invalidate_cache()
        self.assertFalse(self.global_leave01.id in
                         self.calendar01.leave_ids.ids)
