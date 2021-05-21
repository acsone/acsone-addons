# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo.modules.module import get_module_resource
import odoo.tests.common as common


def load_file(cr, module, *args):
    tools.convert_file(
        cr, 'account_wallet',
        get_module_resource(module, *args),
        {},
        'init',
        False,
        'test')


class WalletCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(WalletCommon, cls).setUpClass()
        load_file(
            cls.cr,
            'account_wallet',
            'tests/data/',
            'account_wallet_data.xml')
        cls.wallet_obj = cls.env['account.wallet']
        cls.account = cls.env.ref('account_wallet.wallet')
        cls.partner_account = cls.env['account.account'].search([
            ('user_type_id.type', '=', 'receivable')
        ], limit=1)
        cls.wallet_journal = cls.env.ref('account_wallet.wallet_journal')
        cls.wallet_type = cls.env.ref('account_wallet.wallet_type')
        vals = {
            'wallet_type_id': cls.wallet_type.id,
        }
        cls.wallet = cls.wallet_obj.create(vals)

    def _provision_wallet(self, amount, wallet=None):
        if not wallet:
            wallet = self.wallet
        vals = {
            'name': 'Credit Wallet',
            'journal_id': wallet.account_wallet_type_id.journal_id.id,
        }
        self.move = self.env['account.move'].create(vals)
        vals = {
            'name': 'Credit Wallet',
            'credit': amount,
            'debit': 0,
            'account_wallet_id': wallet.id,
            'account_id': self.account.id,
            'move_id': self.move.id,
        }
        self.env['account.move.line'].with_context(
            check_move_validity=False).create(vals)
        vals = {
            'name': 'Credit Wallet',
            'credit': 0,
            'debit': amount,
            'account_id': self.partner_account.id,
            'move_id': self.move.id,
        }
        self.env['account.move.line'].create(vals)
        self.move.post()
