# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = "hr.contract"

    contract_signed = fields.Boolean(
        help='Set this when the contract is signed by the contractor')
    signature_date = fields.Date()

    @api.onchange('signature_date')
    @api.one
    def onchange_signature_date(self):
        if self.signature_date:
            self.contract_signed = True
