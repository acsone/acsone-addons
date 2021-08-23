# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_wallet_with_coupon = fields.Boolean(
        compute='_compute_is_wallet_with_coupon',
        help="This is a technical field in order to determine if the"
        "journal is a Wallet one and force the usage of Coupon.")
    check_cagnotte_amount = fields.Boolean(
        compute='_compute_check_cagnotte_amount')

    def _compute_is_wallet_with_coupon(self):
        AcountWalletTypeObj = self.env['account.wallet.type']
        for journal in self:
            wallet_type_count = AcountWalletTypeObj.search_count([
                ('journal_id', '=', journal.id),
                ('with_coupon_code', '=', True)
            ])
            journal.is_wallet_with_coupon = wallet_type_count > 0

    def _compute_check_cagnotte_amount(self):
        CagnotteTypeObj = self.env['cagnotte.type']
        for journal in self:
            cagnotte_type_count = CagnotteTypeObj.search_count([
                ('journal_id', '=', journal.id),
                ('with_coupon_code', '=', True),
                ('no_negative', '=', True)
            ])
            journal.check_cagnotte_amount = cagnotte_type_count > 0
