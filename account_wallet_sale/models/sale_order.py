# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    has_wallet = fields.Boolean(
        compute="_compute_has_wallet",
        help="This is used to check if sale order lines contain wallet",
    )

    def _reapply_wallet(self):
        """
        If sale order contains a line with wallet, save it, unlink the
        corresponding lines and then apply wallet.
        This is typically used when sale order lines have changed and we
        need to check if the wallet is still applicable.
        :return:
        """
        for sale in self.filtered(
                lambda s: s.state == 'draft' and s.has_wallet):
            wallet_lines = self.mapped(
                'order_line').filtered('account_wallet_id')
            wallet_to_reapply = {}
            i = 0
            for wallet in wallet_lines.sorted(
                    key=lambda s: s.price_total, reverse=True):
                wallet_to_reapply[i] = \
                    wallet.account_wallet_id
                i += 1
            sale.unset_wallet()
            # Ensure to apply cagnottes with greater amounts first
            for key, wallet in sorted(wallet_to_reapply.items()):
                sale.apply_wallet(wallet)

    def write(self, vals):
        res = super().write(vals)
        if 'order_line' in vals:
            self._reapply_wallet()
        return res

    @api.depends('order_line', 'order_line.account_wallet_id')
    def _compute_has_wallet(self):
        sale_wallet = self.filtered('order_line.account_wallet_id')
        for sale in sale_wallet:
            sale.has_wallet = True
        (self - sale_wallet).has_wallet = False

    def _get_wallet_usable_amount(self, wallet):
        """
        This is the usable amount of wallet
        :param wallet:
        :return:
        """
        if self.amount_total >= wallet.balance:
            return wallet.balance
        return self.amount_total

    def unset_wallet(self):
        for line in self.mapped('order_line'):
            if line.account_wallet_id:
                line.unlink()

    def _get_wallet_applicable_sales(self):
        """
        We cannot apply a wallet to a confirmed sale order.
        :return:
        """
        return self.filtered(lambda s: s.state == 'draft')

    def apply_wallet(self, wallet):
        """
        Entry point on sale order level to apply wallet balance
        :param wallet:
        :return:
        """
        for sale in self:
            # We check that the sale order value is > 0
            if wallet.balance > 0.0 and sale.amount_total > 0.0:
                sale._generate_wallet_line(wallet)

    @api.model
    def _prepare_wallet_line(self, order, wallet):
        vals = {
            'product_id': wallet.wallet_type_id.product_id,
            'name': wallet._get_name(),
            'product_uom_qty': -1.0,
            'product_uom': wallet.wallet_type_id.product_id.uom_id.id,
            'order_id': order.id,
            'account_wallet_id': wallet.id,
        }
        return vals

    def _get_wallet_line_price(self, line, wallet):
        price_unit = self._get_wallet_usable_amount(wallet)
        return price_unit

    def _generate_wallet_line(self, wallet):
        """
        Generate sale order line corresponding to wallet product
        :param wallet:
        :return:
        """
        self.ensure_one()
        vals = self._prepare_wallet_line(self, wallet)
        line = self.env['sale.order.line'].new(vals)
        line.product_id_change()
        vals = line._convert_to_write(line._cache)
        vals.update({
            'price_unit': self._get_wallet_line_price(line, wallet),
        })
        self.env['sale.order.line'].create(vals)

    def wallet_pay(self):
        """
        Action for wizard to pay with wallet
        :return:
        """
        action_rec = self.env.ref(
            'account_wallet_sale.action_view_sale_wallet_pay')
        if action_rec:
            action = action_rec.read([])[0]
            action['views'] = [
                (view_id, mode) for (view_id, mode) in
                action['views'] if mode == 'form'] or action['views']
            action['context'] = {
                'default_sale_order_id': self.id,
            }
            return action
