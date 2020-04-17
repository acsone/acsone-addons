# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cagnotte_type_id = fields.Many2one(
        comodel_name='cagnotte.type',
        string='Cagnotte type',
        readonly=True,
        ondelete='restrict',
        help="Use this field to give coupon to a customer",
        states={'draft': [('readonly', False)]}
    )

    @api.onchange("cagnotte_type_id")
    def onchange_cagnotte_type_id(self):
        if self.cagnotte_type_id:
            self.account_id = self.cagnotte_type_id.account_id
