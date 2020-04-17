# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo.modules.module import get_module_resource
import odoo.tests.common as common


def load_file(cr, module, *args):
    tools.convert_file(
        cr, 'cagnotte_base',
        get_module_resource(module, *args),
        {},
        'init',
        False,
        'test')


class TestCagnotte(common.TransactionCase):

    def setUp(self):
        super(TestCagnotte, self).setUp()
        load_file(
            self.cr,
            'cagnotte_base',
            'tests/data/',
            'account_cagnotte_data.xml')

    def test_cagnotte(self):
        """ Buy cagnotte product
            Check cagnotte amount
            Pay with cagnotte
            Check cagnotte amount
            Try to pay with more than available
            Check error
        """
        cagnotte_type = self.env.ref("cagnotte_base.cagnotte_type")
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)
        invoice = self.env["account.invoice"].create(
            {'partner_id': self.env.ref("base.res_partner_2").id,
             'account_id': invoice_account.id})
        self.env["account.invoice.line"].create(
            {'product_id': cagnotte_type.product_id.id,
             'account_id': cagnotte_type.account_id.id,
             'quantity': 1,
             'price_unit': 100,
             'invoice_id': invoice.id,
             'name': 'set 100 in my cagnotte'})
        invoice.action_invoice_open()
        has_cagnotte = False
        for line in invoice.move_id.line_ids:
            if line.account_id.id == cagnotte_type.account_id.id:
                cagnotte = line.account_cagnotte_id
                self.assertTrue(cagnotte.cagnotte_type_id.id,
                                cagnotte_type.id)
                has_cagnotte = True
        self.assertTrue(has_cagnotte)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 100.00, 2)

        move_obj = self.env["account.move"]

        move_obj.create(
            {"journal_id": cagnotte.cagnotte_type_id.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": cagnotte.cagnotte_type_id.account_id.id,
                     "account_cagnotte_id": cagnotte.id,
                     "name": "payment with my cagnotte",
                     "debit": 100
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "payment with my cagnotte",
                     "credit": 100})]})
        self.assertEqual(len(cagnotte.account_move_line_ids), 2)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 0.00, 2)
