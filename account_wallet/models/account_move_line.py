# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND
from odoo.tools import float_compare
from odoo.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_wallet_id = fields.Many2one(
        comodel_name="account.wallet",
        string="Wallet",
        ondelete="restrict",
        index=True,
    )

    def _get_computed_account(self):
        if self.account_wallet_id:
            return self.account_wallet_id.wallet_type_id.account_id
        return super()._get_computed_account()

    @api.onchange("account_wallet_id")
    def _onchange_account_wallet_id(self):
        for line in self.filtered("account_wallet_id"):
            line.account_id = line._get_computed_account()
            partner = line.account_wallet_id.partner_id
            if partner:
                line.partner_id = partner

    def _get_wallet_domain(self, values):
        domain = [("wallet_type_id.account_id", "=", values["account_id"])]
        if values.get("partner_id"):
            domain = AND([domain, [("partner_id", "=", values["partner_id"])]])
        return domain

    def _get_account_wallet_type(self, values):
        if values.get("account_id"):
            wallet_type = self.env["account.wallet.type"].search(
                [("account_id", "=", values["account_id"])]
            )
            return wallet_type

    def _prepare_account_wallet_values(self, values):
        wallet_type = self._get_account_wallet_type(values)
        vals = {}
        if wallet_type:
            vals.update(
                {
                    "wallet_type_id": wallet_type.id,
                }
            )
        return vals

    def wallet_value(self, vals_list):
        """If used account is on a wallet type,
        create a wallet
        """
        wallet_obj = self.env["account.wallet"]
        for values in vals_list:
            if not values.get("account_wallet_id"):
                #  check if account/partner is linked to cagnotte and assign it
                # if it the case
                wallet = wallet_obj.search(self._get_wallet_domain(values))
                if wallet:
                    values["account_wallet_id"] = wallet.id
                else:
                    # If we try to feed the wallet and none is found, create it
                    comp = float_compare(
                        values.get("credit", 0.0), 0.0, precision_digits=2
                    )
                    if values.get("account_id") and comp != 0:
                        wallet_values = self._prepare_account_wallet_values(values)
                        if wallet_values:
                            # create wallet
                            values["account_wallet_id"] = (
                                self.env["account.wallet"].create(wallet_values).id
                            )
            elif values.get("account_wallet_id"):
                wallet = wallet_obj.browse(values["account_wallet_id"])
                values["partner_id"] = wallet.partner_id.id or values.get("partner_id")
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self.wallet_value(vals_list)
        return super().create(vals_list)

    @api.constrains("account_wallet_id", "account_id")
    def _check_wallet_account(self):
        """Account must correspond to wallet account"""
        if any(
            line.account_wallet_id
            and line.account_wallet_id.wallet_type_id.account_id != line.account_id
            for line in self
        ):
            raise ValidationError(
                _("The account doesn't correspond" " to the wallet account")
            )
        return True
