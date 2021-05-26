# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountCagnotte(models.Model):

    _inherit = 'account.cagnotte'

    solde_cagnotte = fields.Monetary(
        compute='_compute_solde_cagnotte',
    )
    sale_order_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="account_cagnotte_id",
    )
    sale_order_line_not_invoiced_ids = fields.One2many(
        compute="_compute_sale_order_line_not_invoiced_ids",
        comodel_name="sale.order.line",
    )
    sale_order_balance = fields.Monetary(
        compute="_compute_sale_order_balance",
        currency_field='company_currency_id',
    )

    @api.multi
    @api.depends(
        "sale_order_line_ids.invoice_lines.invoice_id.move_id.line_ids")
    def _compute_sale_order_line_not_invoiced_ids(self):
        for cagnotte in self:
            lines_not_invoiced = cagnotte.sale_order_line_ids.filtered(
                lambda l: not l.invoice_lines.mapped(
                    'invoice_id.move_id.line_ids').filtered(
                    'account_cagnotte_id'))
            cagnotte.sale_order_line_not_invoiced_ids = lines_not_invoiced

    @api.multi
    @api.depends(
        "sale_order_line_not_invoiced_ids",
        "sale_order_line_ids.order_id.state")
    def _compute_sale_order_balance(self):
        """
        We get all sale order lines that are not concerned by
        linked account move lines.
        Then,
        :return:
        """
        for cagnotte in self.filtered("sale_order_line_not_invoiced_ids"):
            cagnotte.sale_order_balance = sum(
                cagnotte.sale_order_line_not_invoiced_ids.filtered(
                    lambda l: l.order_id.state != "cancel").mapped(
                    'price_total'))

    @api.multi
    @api.depends('account_move_line_ids.debit',
                 'account_move_line_ids.credit',
                 'sale_order_line_ids',
                 'sale_order_line_ids.order_id',
                 'sale_order_line_ids.order_id.state',
                 'sale_order_balance')
    def _compute_solde_cagnotte(self):
        super(AccountCagnotte, self)._compute_solde_cagnotte()
        for cagnotte in self.filtered('sale_order_balance'):
            cagnotte.solde_cagnotte += cagnotte.sale_order_balance

    @api.multi
    def action_open_cagnotte_sale_lines(self):
        """
        Action to get sale orders with pending cagnotte lines (not invoiced)
        :return:
        """
        self.ensure_one()
        sale_orders = self.sale_order_line_not_invoiced_ids.mapped("order_id")
        action_rec = self.env.ref(
            'cagnotte_sale.action_orders_cagnotte_not_invoiced')
        if action_rec:
            action = action_rec.read([])[0]
            action['views'] = [
                (view_id, mode) for (view_id, mode) in
                action['views'] if mode == 'tree'] or action['views']
            action['domain'] = [('id', 'in', sale_orders.ids)]
            return action
