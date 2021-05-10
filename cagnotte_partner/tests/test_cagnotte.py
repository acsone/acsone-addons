# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .common import CagnotteCommonPartner
from odoo.exceptions import ValidationError


class TestCagnotte(CagnotteCommonPartner):

    def test_cagnotte(self):
        """ Create cagnotte with partner
            Use cagnotte
            check partner is on account move
        """
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)

        move_obj = self.env["account.move"]

        cag_move = move_obj.create({
            "journal_id": self.cagnotte_type.journal_id.id,
            "line_ids": [
                (0, 0, {
                    "account_id": self.cagnotte_type.account_id.id,
                    "account_cagnotte_id": self.cagnotte.id,
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
        self.assertEqual(line.partner_id.id, self.partner.id)
        self.assertAlmostEqual(self.cagnotte.solde_cagnotte, 100.00, 2)

        move_obj.create(
            {"journal_id": self.cagnotte_type.journal_id.id,
             "line_ids": [
                 (0, 0, {
                     "account_id": self.cagnotte_type.account_id.id,
                     "partner_id": self.partner.id,
                     "account_cagnotte_id": self.cagnotte.id,
                     "name": "payement with my cagnotte",
                     "debit": 20
                 }),
                 (0, 0, {
                     "account_id": invoice_account.id,
                     "name": "payement with my cagnotte",
                     "credit": 20})]})

        self.assertAlmostEqual(self.cagnotte.solde_cagnotte, 80.00, 2)

    def test_cagnotte_unique(self):
        with self.assertRaises(ValidationError):
            self.cagnotte_obj.create(
                {'cagnotte_type_id': self.cagnotte_type.id,
                 'partner_id': self.partner.id})

        cagnotte2 = self.cagnotte_obj.create(
            {'cagnotte_type_id': self.cagnotte_type.id,
             'partner_id': self.partner.id,
             'active': False})

        with self.assertRaises(ValidationError):
            cagnotte2.write({'active': True})

        self.cagnotte.write({'active': False})
