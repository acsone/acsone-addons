# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    account_wallet_type_id = fields.Many2one(
        comodel_name='account.wallet.type',
        string='Wallet type',
        readonly=True,
        ondelete='restrict',
        help="Use this field to give coupon to a customer",
        states={'draft': [('readonly', False)]}
    )

    @api.onchange("account_wallet_type_id")
    def onchange_account_wallet_type_id(self):
        if self.account_wallet_type_id:
            self.account_id = self.account_wallet_type_id.account_id

    def invoice_line_move_line_get(self):
        """
        Create move line with cagnotte id if needed
        :return:
        """
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        wallet_lines = self.invoice_line_ids.filtered("account_cagnotte_id")
        for line_val in res:
            invl_id = line_val.get("invl_id")
            if invl_id in wallet_lines.ids:
                line_val.update({
                    "account_cagnotte_id": wallet_lines.filtered(
                        lambda c, l_id=invl_id: c.id == l_id).mapped(
                        "account_wallet_id").id})
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        wallet_id = line.get("account_cagnotte_id")
        if wallet_id:
            res.update({"account_wallet_id": wallet_id})
        return res
