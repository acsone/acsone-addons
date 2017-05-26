# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.addons.cagnotte_base.tests.test_cagnotte import load_file


class TestCagnotte(common.TransactionCase):

    def setUp(self):
        super(TestCagnotte, self).setUp()
        load_file(
            self.cr,
            'cagnotte_base',
            'tests/data/',
            'account_cagnotte_data.xml')

    def test_cagnotte(self):
        """ Create cagnotte with partner
            Use cagnotte
            check partner is on account move
        """
        cagnotte_type = self.env.ref("cagnotte_base.cagnotte_type")
        cagnotte_partner = self.env.ref("base.res_partner_3")
        cagnotte_obj = self.env['account.cagnotte']
        cagnotte = cagnotte_obj.create({'cagnotte_type_id': cagnotte_type.id,
                                        'partner_id': cagnotte_partner.id})
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)

        move_obj = self.env["account.move"]

        cag_move = move_obj.create(
            {"journal_id": cagnotte_type.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": cagnotte_type.account_id.id,
                     "account_cagnotte_id": cagnotte.id,
                     "name": "get credit on my cagnotte",
                     "credit": 100
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "get credit on my cagnotte",
                     "debit": 100})]})

        line = self.env['account.move.line'].search([
            ('move_id', '=', cag_move.id),
            ('credit', '=', 100)
        ])
        self.assertEqual(line.partner_id.id,
                         cagnotte_partner.id)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 100.00, 2)

        move_obj.create(
            {"journal_id": cagnotte_type.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": cagnotte_type.account_id.id,
                     "partner_id": cagnotte_partner.id,
                     "account_cagnotte_id": cagnotte.id,
                     "name": "payement with my cagnotte",
                     "debit": 20
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "payement with my cagnotte",
                     "credit": 20})]})

        self.assertAlmostEqual(cagnotte.solde_cagnotte, 80.00, 2)
