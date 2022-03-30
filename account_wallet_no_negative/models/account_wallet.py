# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class AccountWallet(models.Model):

    _inherit = "account.wallet"

    no_negative = fields.Boolean(
        tracking=True,
        default=lambda self: self.wallet_type_id.no_negative,
    )
    is_negative = fields.Boolean(
        compute="_compute_is_negative",
        store=True,
    )

    @api.onchange("wallet_type_id")
    def _onchange_wallet_type_id(self):
        for wallet in self:
            if not wallet.no_negative:
                wallet.no_negative = wallet.wallet_type_id.no_negative

    @api.constrains("balance", "no_negative")
    def _check_no_negative(self):
        for wallet in self.filtered("no_negative"):
            rounding = wallet.company_currency_id.rounding
            compare = float_compare(wallet.balance, 0, precision_rounding=rounding)
            if compare < 0:
                raise ValidationError(_("The wallet balance cannot be negative !"))

    @api.depends("balance")
    def _compute_is_negative(self):
        negative_wallets = self.filtered(lambda c: c.balance < 0)
        negative_wallets.update({"is_negative": True})

    @api.model
    def _update_vals_no_negative(self, vals_list):
        for vals in vals_list:
            if "wallet_type_id" in vals and "no_negative" not in vals:
                wallet_type = self.env["account.wallet.type"].browse(
                    vals["wallet_type_id"]
                )
                vals.update({"no_negative": wallet_type.no_negative})
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        self._update_vals_no_negative(vals_list)
        return super().create(vals_list)
