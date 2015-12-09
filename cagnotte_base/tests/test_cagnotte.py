# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common
from openerp.exceptions import ValidationError


class TestCagnotte(common.TransactionCase):

    def test_cagnotte(self):
        """ Buy cagnotte product
            Check cagnotte amount
            Pay with cagnotte
            Check cagnotte amount
            Try to pay with more than available
            Check error
        """
        cagnotte_type = self.env.ref("cagnotte_base.cagnotte_type")
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
        has_cagnotte = False
        cagnotte = self.env['account.cagnotte']
        for line in invoice.move_id.line_id:
            if line.account_id.id == cagnotte_type.account_id.id:
                cagnotte = line.account_cagnotte_id
                self.assertTrue(cagnotte.cagnotte_type_id.id,
                                cagnotte_type.id)
                has_cagnotte = True
        self.assertTrue(has_cagnotte)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 100.00, 2)

        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]

        pay_move = move_obj.create(
            {"journal_id": cagnotte.cagnotte_type_id.journal_id.id})
        pay_move_line = move_line_obj.create(
            {"move_id": pay_move.id,
             "account_id": cagnotte.cagnotte_type_id.account_id.id,
             "account_cagnotte_id": cagnotte.id,
             "name": "payement with my cagnotte",
             "debit": 100})
        self.assertEqual(len(cagnotte.account_move_line_ids), 2)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 0.00, 2)

        try:
            pay_move_line.debit = 150
        except ValidationError, e:
            self.assertEqual(
                e.value, "Field(s) `account_cagnotte_id, credit, debit` "
                         "failed against a constraint: The cagnotte "
                         "amount is insufficient")
        else:
            assert False, "Not enough cagnotte amount"
