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

    def invoice_line_move_line_get(self):
        """
        Create move line with cagnotte id if needed
        :return:
        """
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        cagnotte_lines = self.invoice_line_ids.filtered("account_cagnotte_id")
        for line_val in res:
            invl_id = line_val.get("invl_id")
            if invl_id in cagnotte_lines.ids:
                line_val.update({
                    "account_cagnotte_id": cagnotte_lines.filtered(
                        lambda c, l_id=invl_id: c.id == l_id).mapped(
                        "account_cagnotte_id").id})
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        cagnotte_id = line.get("account_cagnotte_id")
        if cagnotte_id:
            res.update({"account_cagnotte_id": cagnotte_id})
        return res
