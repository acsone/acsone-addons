# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.fields import first
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    has_cagnotte = fields.Boolean(
        compute="_compute_has_cagnotte",
        help="This is used to check if sale order lines contain cagnotte",
    )
    order_line = fields.One2many(
        inverse="_inverse_order_line"
    )

    @api.multi
    def _reapply_cagnotte(self):
        for sale in self.filtered('has_cagnotte'):
            cagnotte_line = first(
                self.mapped('order_line').filtered('account_cagnotte_id'))
            cagnotte = cagnotte_line.account_cagnotte_id
            sale.unset_cagnotte()
            sale.apply_cagnotte(cagnotte)

    @api.multi
    def _inverse_order_line(self):
        # This is triggered on sale order level but is not sufficent
        # as if the order line is created by another mean (than e.g. interface)
        # this is not triggered (as well as write())
        self._reapply_cagnotte()

    @api.multi
    @api.depends('order_line.account_cagnotte_id')
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
        self.mapped('order_line').filtered('account_cagnotte_id').unlink()

    @api.multi
    def apply_cagnotte(self, cagnotte):
        for sale in self:
            if cagnotte.partner_id != sale.partner_id:
                raise UserError(_('The cagnotte you try to use is not yours!'))
            # We check that the sale order value is > 0
            if cagnotte.solde_cagnotte > 0.0 and self.amount_total > 0.0:
                sale._generate_cagnotte_line(cagnotte)

    @api.model
    def _prepare_cagnotte_line(self, order, cagnotte):
        vals = {
            'product_id': cagnotte.cagnotte_type_id.product_id,
            'name': cagnotte.name,
            'product_uom_qty': -1.0,
            'product_uom': cagnotte.cagnotte_type_id.product_id.uom_id.id,
            'order_id': order.id,
            'price_unit': self._get_cagnotte_usable_amount(cagnotte),
            'account_cagnotte_id': cagnotte.id,
        }
        return vals

    @api.multi
    def _generate_cagnotte_line(self, cagnotte):
        self.ensure_one()
        vals = self._prepare_cagnotte_line(self, cagnotte)
        line = self.env['sale.order.line'].new(vals)
        line.product_id_change()
        vals = line._convert_to_write(line._cache)
        vals.update({
            'price_unit': self._get_cagnotte_usable_amount(cagnotte),
        })
        self.env['sale.order.line'].create(vals)
