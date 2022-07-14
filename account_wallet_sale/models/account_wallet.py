# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountWallet(models.Model):

    _inherit = "account.wallet"

    sale_order_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="account_wallet_id",
    )
    sale_order_line_not_invoiced_ids = fields.One2many(
        compute="_compute_sale_order_line_not_invoiced_ids",
        comodel_name="sale.order.line",
    )
    sale_order_balance = fields.Monetary(
        compute="_compute_sale_order_balance",
        currency_field="company_currency_id",
    )

    @api.depends("sale_order_line_ids.invoice_lines")
    def _compute_sale_order_line_not_invoiced_ids(self):
        for wallet in self:
            lines_not_invoiced = wallet.sale_order_line_ids.filtered(
                lambda l: not l.invoice_lines.filtered("account_wallet_id")
            )
            wallet.sale_order_line_not_invoiced_ids = lines_not_invoiced

    @api.depends(
        "sale_order_line_not_invoiced_ids", "sale_order_line_ids.order_id.state"
    )
    def _compute_sale_order_balance(self):
        """
        We get all sale order lines that are not concerned by
        linked account move lines.
        Then,
        :return:
        """
        lines_not_invoices = self.filtered("sale_order_line_not_invoiced_ids")
        for wallet in lines_not_invoices:
            wallet.sale_order_balance = sum(
                wallet.sale_order_line_not_invoiced_ids.filtered(
                    lambda l: l.order_id.state != "cancel"
                ).mapped("price_total")
            )
        (self - lines_not_invoices).sale_order_balance = 0.0

    @api.model
    def _get_compute_balance_fields(self):
        res = super()._get_compute_balance_fields()
        sale_fields = [
            "sale_order_line_ids",
            "sale_order_line_ids.order_id",
            "sale_order_line_ids.order_id.state",
            "sale_order_balance",
        ]
        for field in sale_fields:
            if field not in res:
                res.append(field)
        return res

    def _compute_balance(self):
        super()._compute_balance()
        for wallet in self.filtered("sale_order_balance"):
            wallet.balance += wallet.sale_order_balance

    def action_open_wallet_sale_lines(self):
        """
        Action to get sale orders with pending wallet lines (not invoiced)
        :return:
        """
        self.ensure_one()
        sale_orders = self.sale_order_line_not_invoiced_ids.mapped("order_id")
        action_rec = self.env.ref(
            "account_wallet_sale.action_orders_wallet_not_invoiced"
        )
        if action_rec:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account_wallet_sale.action_orders_wallet_not_invoiced"
            )
            action["views"] = [
                (view_id, mode) for (view_id, mode) in action["views"] if mode == "tree"
            ] or action["views"]
            action["domain"] = [("id", "in", sale_orders.ids)]
            return action
