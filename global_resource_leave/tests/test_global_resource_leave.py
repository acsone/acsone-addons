# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


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
