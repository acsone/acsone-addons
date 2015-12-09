# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

import openerp.tests.common as common
from openerp import fields


class TestCagnotte(common.TransactionCase):

    def test_cagnotte(self):
        """ Buy cagnotte product
            Set expiration in past on my cagnotte
            Run cron
            Check Cagnotte is inactive
            Check Cagnotte amount is 0
        """
        cagnotte_type = self.env.ref(
            "cagnotte_expiration.expiration_cagnotte_type")
        invoice = self.env["account.invoice"].create(
            {'partner_id': self.env.ref("base.res_partner_2").id,
             'account_id': self.env.ref("account.a_recv").id})
        self.env["account.invoice.line"].create(
            {'product_id': cagnotte_type.product_id.id,
             'account_id': cagnotte_type.account_id.id,
             'quantity': 1,
             'price_unit': 100,
             'invoice_id': invoice.id,
             'name': 'set 100 in my cagnotte'})
        invoice.signal_workflow('invoice_open')
        cagnotte = self.env['account.cagnotte']
        for line in invoice.move_id.line_id:
            if line.account_id.id == cagnotte_type.account_id.id:
                cagnotte = line.account_cagnotte_id

        date_today = fields.Date.from_string(fields.Date.today())
        expiration_date = date_today + timedelta(days=5)
        self.assertEqual(cagnotte.expiration_date,
                         fields.Date.to_string(expiration_date))

        passed_date = date_today + timedelta(days=-5)
        cagnotte.expiration_date = passed_date

        self.env["account.cagnotte"]._run_expiration_cagnotte()

        self.assertFalse(cagnotte.active)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 0.00, 2)
        self.assertEqual(len(cagnotte.account_move_line_ids), 2)
