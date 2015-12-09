# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestCagnotte(common.TransactionCase):

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

        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]

        cag_move = move_obj.create(
            {"journal_id": cagnotte_type.journal_id.id})
        cag_move_line = move_line_obj.create(
            {"move_id": cag_move.id,
             "account_id": cagnotte_type.account_id.id,
             "account_cagnotte_id": cagnotte.id,
             "name": "payement with my cagnotte",
             "credit": 100})
        self.assertEqual(cag_move_line.partner_id.id, cagnotte_partner.id)
        self.assertAlmostEqual(cagnotte.solde_cagnotte, 100.00, 2)
