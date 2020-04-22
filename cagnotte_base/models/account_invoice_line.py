# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    account_cagnotte_id = fields.Many2one(
        comodel_name="account.cagnotte",
        ondelete="restrict",
    )
