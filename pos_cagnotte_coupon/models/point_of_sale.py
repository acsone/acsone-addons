# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class POSOrderLine(models.Model):
    _inherit = "pos.order.line"

    account_cagnotte_id = fields.Many2one('account.cagnotte', 'Cagnotte')

    @api.model
    def create(self, values):
        if values.get('product_id') and not values.get('account_cagnotte_id'):
            cagnotte_type = self.env['cagnotte.type'].search(
                [('product_id', '=', values['product_id'])])
            if cagnotte_type:
                # create cagnotte
                values['account_cagnotte_id'] = \
                    self.env['account.cagnotte'].create(
                        {'cagnotte_type_id': cagnotte_type.id}).id
        return super(POSOrderLine, self).create(values)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_product_key(self, values):
        product_key = super(PosOrder, self)._get_product_key(values)
        return product_key + (values['account_cagnotte_id'], )

    @api.model
    def _get_product_values(self, line, income_account, amount, tax_code_id,
                            tax_amount, order):
        res = super(PosOrder, self)._get_product_values(
            line, income_account, amount, tax_code_id, tax_amount, order)
        res['account_cagnotte_id'] = line.account_cagnotte_id.id
        return res

    @api.model
    def _payment_fields(self, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(ui_paymentline)
        res['account_cagnotte_id'] = ui_paymentline.get('account_cagnotte_id')
        return res

    @api.model
    def _add_custom_payment_line_info(self, order_id, data):
        res = super(PosOrder, self)._add_custom_payment_line_info(order_id,
                                                                  data)
        res['account_cagnotte_id'] = data.get('account_cagnotte_id')
        return res
