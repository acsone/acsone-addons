# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_account_move_line_product_key(self, values):
        product_key = super()._get_account_move_line_product_key(values)
        account_wallet_id = values.get("account_wallet_id")
        if account_wallet_id:
            product_key += (values.get("account_wallet_id"),)
        return product_key

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        res = super()._payment_fields(order, ui_paymentline)
        res["account_wallet_id"] = ui_paymentline.get("account_wallet_id")
        return res

    def _prepare_bank_statement_line_payment_values(self, data):
        values = super(PosOrder, self)._prepare_bank_statement_line_payment_values(data)
        values["account_wallet_id"] = data.get("account_wallet_id")
        return values

    @api.model
    def _prepare_product_account_move_line(
        self, line, partner_id, account_id, taxe_ids
    ):
        values = super()._prepare_product_account_move_line(
            line, partner_id, account_id, taxe_ids
        )
        if not values.get("account_wallet_id"):
            values["account_wallet_id"] = getattr(line.account_wallet_id, "id", False)
        return values

    def _prepare_invoice_line(self, order_line):
        """
        As wallet feed depends on accounting entries, if we sell a wallet
        product, we should invoice pos order to get correct balance.
        TODO: fill the gap by feeding accounting entries with normal
        pos orders (without invoicing).
        """
        res = super()._prepare_invoice_line(order_line)
        if order_line.account_wallet_id:
            res.update({"account_wallet_id": order_line.account_wallet_id.id})
        return res
