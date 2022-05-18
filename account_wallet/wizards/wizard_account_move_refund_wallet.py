# Copyright 2022 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class AccountMoveRefund(models.TransientModel):

    _name = "wizard.account_move_refund.wallet"
    _description = "Refund By Wallet"

    account_wallet_type_id = fields.Many2one(
        comodel_name="account.wallet.type",
        string="Wallet type",
        required=True,
        ondelete="cascade",
    )

    amount = fields.Float(required=True, ondelete="cascade")

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer", required=True, ondelete="cascade"
    )

    invoice_date = fields.Date(string="Invoice Date", default=fields.Date.today)

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        ondelete="cascade",
    )

    def apply(self):
        self.ensure_one()
        old_account = self.partner_id.property_account_receivable_id
        try:
            self.partner_id.property_account_receivable_id = (
                self.account_wallet_type_id.account_id
            )

            values = {
                "partner_id": self.partner_id.id,
                "invoice_date": self.invoice_date,
                "move_type": "out_refund",
                "account_wallet_type_id": self.account_wallet_type_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_id.id,
                            "quantity": 1,
                            "price_unit": self.amount,
                            "name": self.product_id.display_name,
                        },
                    ),
                ],
            }
            move = self.env["account.move"].create(values)
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
