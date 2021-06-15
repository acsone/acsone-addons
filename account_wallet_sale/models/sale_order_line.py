# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    account_wallet_id = fields.Many2one(
        comodel_name='account.wallet',
        ondelete='restrict',
        index=True,
    )

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if "account_wallet_id" not in vals:
            res.order_id._reapply_wallet()
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        """
        To correctly apply the wallet name (and not the product one)
        :return:
        """
        res = super().product_id_change()
        if self.account_wallet_id:
            self.name = self.account_wallet_id._get_name()
        return res

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if self.account_wallet_id:
            res['account_wallet_id'] = self.account_wallet_id.id
        return res
