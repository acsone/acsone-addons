# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    has_cagnotte = fields.Boolean(compute='_compute_has_cagnotte')
    check_cagnotte_amount = fields.Boolean(
        compute='_compute_check_cagnotte_amount')

    @api.multi
    def _compute_has_cagnotte(self):
        CagnotteTypeObj = self.env['cagnotte.type']
        for journal in self:
            cagnotte_type_count = CagnotteTypeObj.search_count([
                ('journal_id', '=', journal.id),
                ('with_coupon_code', '=', True)
            ])
            journal.has_cagnotte = cagnotte_type_count > 0

    @api.multi
    def _compute_check_cagnotte_amount(self):
        CagnotteTypeObj = self.env['cagnotte.type']
        for journal in self:
            cagnotte_type_count = CagnotteTypeObj.search_count([
                ('journal_id', '=', journal.id),
                ('with_coupon_code', '=', True),
                ('no_negative', '=', True)
            ])
            journal.check_cagnotte_amount = cagnotte_type_count > 0
