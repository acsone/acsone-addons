# Copyright 2022 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class AccountMoveCreditNote(models.TransientModel):

    _name = "wizard.account_move_credit_notes.wallet"
    _description = "Credit Note By Wallet"

    def _get_default_product_id(self):
        config = self.env["ir.config_parameter"]
        param = "account_move_credit_notes_wallet_default_product"
        default_product_id = config.sudo().get_param(param)
        product = self.env["product.product"].browse()
        if default_product_id:
            product = self.env["product.product"].browse(int(default_product_id))
        return product

    account_wallet_type_id = fields.Many2one(
        comodel_name="account.wallet.type",
        string="Wallet type",
        required=True,
        ondelete="cascade",
    )

    amount = fields.Float(required=True)

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer", required=True, ondelete="cascade"
    )

    invoice_date = fields.Date(string="Invoice Date", default=fields.Date.today)

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        ondelete="cascade",
        domain="[('type', '=', 'service')]",
        default=_get_default_product_id,
    )

    def _prepare_move_values(self):
        line_values = self._prepare_move_line_values()
        values = {
            "partner_id": self.partner_id.id,
            "invoice_date": self.invoice_date,
            "move_type": "out_refund",
            "account_wallet_type_id": self.account_wallet_type_id.id,
            "invoice_line_ids": line_values,
        }
        return values

    def _prepare_move_line_values(self):
        values = [
            (
                0,
                False,
                {
                    "product_id": self.product_id.id,
                    "quantity": 1,
                    "price_unit": self.amount,
                    "name": self.product_id.display_name,
                },
            )
        ]
        return values

    def apply(self):
        self.ensure_one()
        old_account = self.partner_id.property_account_receivable_id
        try:
            self.partner_id.property_account_receivable_id = (
                self.account_wallet_type_id.account_id
            )

            values = self._prepare_move_values()
            move = self.env["account.move"].create(values)
            move.action_post()
        finally:
            self.partner_id.property_account_receivable_id = old_account

        return {
            "name": _("Credit Note"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": move.id,
        }
