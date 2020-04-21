# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
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


class CagnotteCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(CagnotteCommon, cls).setUpClass()
        load_file(
            cls.cr,
            'cagnotte_base',
            'tests/data/',
            'account_cagnotte_data.xml')
        cls.cagnotte_obj = cls.env['account.cagnotte']
        cls.account = cls.env.ref('cagnotte_base.cagnotte')
        cls.partner_account = cls.env['account.account'].search([
            ('user_type_id.type', '=', 'receivable')
        ], limit=1)
        cls.cagnotte_journal = cls.env.ref('cagnotte_base.cagnotte_journal')
        cls.cagnotte_type = cls.env.ref('cagnotte_base.cagnotte_type')
        vals = {
            'cagnotte_type_id': cls.cagnotte_type.id,
        }
        cls.cagnotte = cls.cagnotte_obj.create(vals)

    def _provision_cagnotte(self, amount):
        vals = {
            'name': 'Credit Cagnotte',
            'journal_id': self.cagnotte_journal.id,
        }
        self.move = self.env['account.move'].create(vals)
        vals = {
            'name': 'Credit Cagnotte',
            'credit': amount,
            'debit': 0,
            'account_cagnotte_id': self.cagnotte.id,
            'account_id': self.account.id,
            'move_id': self.move.id,
        }
        self.env['account.move.line'].with_context(
            check_move_validity=False).create(vals)
        vals = {
            'name': 'Credit Cagnotte',
            'credit': 0,
            'debit': amount,
            'account_id': self.partner_account.id,
            'move_id': self.move.id,
        }
        self.env['account.move.line'].create(vals)
        self.move.post()
