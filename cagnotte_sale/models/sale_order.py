# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    has_cagnotte = fields.Boolean(
        compute="_compute_has_cagnotte",
        help="This is used to check if sale order lines contain cagnotte",
    )

    @api.multi
    def _reapply_cagnotte(self):
        """
        If sale order contains a line with cagnotte, save it, unlink the
        corresponding lines and then apply cagnotte.
        This is typically used when sale order lines have changed and we
        need to check if the cagnotte is still applicable.
        :return:
        """
        for sale in self.filtered(
                lambda s: s.state == 'draft' and s.has_cagnotte):
            cagnotte_line = first(
                self.mapped('order_line').filtered('account_cagnotte_id'))
            cagnotte = cagnotte_line.account_cagnotte_id
            sale.unset_cagnotte()
            sale.apply_cagnotte(cagnotte)

    def _update_cagnote_vals(self, vals):
        if 'order_line' in vals:
            # Hack to remove the adding value as we are going to remove it in
            # code. The interface would add 'order_line': [(4, <id>)] even
            # for untouched ones.
            line_ids = []
            for line_val in vals.get("order_line"):
                if line_val[0] == 4:
                    line_ids.append(line_val[1])
            lines = self.env["sale.order.line"].browse(
                line_ids).filtered("account_cagnotte_id")
            if lines:
                for line_val in vals.get("order_line"):
                    if line_val[0] == 4 and line_val[1] in lines.ids:
                        vals["order_line"].remove(line_val)
        return vals

    @api.multi
    def write(self, vals):
        self._update_cagnote_vals(vals)
        res = super(SaleOrder, self).write(vals)
        if 'order_line' in vals:
            self._reapply_cagnotte()
        return res

    @api.multi
    @api.depends('order_line', 'order_line.account_cagnotte_id')
    def _compute_has_cagnotte(self):
        for sale in self.filtered('order_line.account_cagnotte_id'):
            sale.has_cagnotte = True

    def _get_cagnotte_usable_amount(self, cagnotte):
        """
        This is the usable amount of cagnotte
        :param cagnotte:
        :return:
        """
        if self.amount_total >= cagnotte.solde_cagnotte:
            return cagnotte.solde_cagnotte
        return self.amount_total

    @api.multi
    def unset_cagnotte(self):
        for line in self.mapped('order_line'):
            if line.account_cagnotte_id:
                line.unlink()

    def _get_cagnotte_applicable_sales(self):
        """
        We cannot apply a cagnotte to a confirmed sale order.
        :return:
        """
        return self.filtered(lambda s: s.state == 'draft')

    @api.multi
    def apply_cagnotte(self, cagnotte):
        """
        Entry point on sale order level to apply cagnotte balance
        :param cagnotte:
        :return:
        """
        for sale in self:
            # We check that the sale order value is > 0
            if cagnotte.solde_cagnotte > 0.0 and sale.amount_total > 0.0:
                sale._generate_cagnotte_line(cagnotte)

    @api.model
    def _prepare_cagnotte_line(self, order, cagnotte):
        vals = {
            'product_id': cagnotte.cagnotte_type_id.product_id,
            'name': cagnotte.name,
            'product_uom_qty': -1.0,
            'product_uom': cagnotte.cagnotte_type_id.product_id.uom_id.id,
            'order_id': order.id,
            'account_cagnotte_id': cagnotte.id,
        }
        return vals

    def _get_cagnotte_line_price(self, line, cagnotte):
        price_unit = self._get_cagnotte_usable_amount(cagnotte)
        return price_unit

    @api.multi
    def _generate_cagnotte_line(self, cagnotte):
        """
        Generate sale order line corresponding to cagnotte product
        :param cagnotte:
        :return:
        """
        self.ensure_one()
        vals = self._prepare_cagnotte_line(self, cagnotte)
        line = self.env['sale.order.line'].new(vals)
        line.product_id_change()
        vals = line._convert_to_write(line._cache)
        vals.update({
            'price_unit': self._get_cagnotte_line_price(line, cagnotte),
        })
        self.env['sale.order.line'].create(vals)

    @api.multi
    def cagnotte_pay(self):
        """
        Action for wizard to pay with cagnotte
        :return:
        """
        action_rec = self.env.ref(
            'cagnotte_sale.action_view_sale_cagnotte_pay')
        if action_rec:
            action = action_rec.read([])[0]
            action['views'] = [
                (view_id, mode) for (view_id, mode) in
                action['views'] if mode == 'form'] or action['views']
            action['context'] = {
                'default_sale_order_id': self.id,
            }
            return action
