# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    account_wallet_type_id = fields.Many2one(
        comodel_name="account.wallet.type",
        string="Wallet type",
        readonly=True,
        ondelete="restrict",
        help="Use this field to give coupon to a customer",
        states={"draft": [("readonly", False)]},
    )

    @api.onchange("account_wallet_type_id")
    def onchange_account_wallet_type_id(self):
        # We have to empty the lines in this case
        # tests made to use the onchange partner_id
        # (which change the account on the lines)
        # but the self.account_wallet_type_id.account_id
        # does not have a user_type_id payable or receivable
        # So it causes problem -> decision made to empty lines
        if self.account_wallet_type_id:
            self.line_ids = False
            self.invoice_line_ids = False

    def _recompute_dynamic_lines(
        self, recompute_all_taxes=False, recompute_tax_base_amount=False
    ):
        if (
            self.partner_id
            and self.is_sale_document(include_receipts=True)
            and self.account_wallet_type_id
        ):
            old_account = self.partner_id.property_account_receivable_id
            self.partner_id.property_account_receivable_id = (
                self.account_wallet_type_id.account_id
            )
            res = super()._recompute_dynamic_lines(
                recompute_all_taxes, recompute_tax_base_amount
            )
            self.partner_id.property_account_receivable_id = old_account
        else:
            res = super()._recompute_dynamic_lines(
                recompute_all_taxes, recompute_tax_base_amount
            )
        return res
