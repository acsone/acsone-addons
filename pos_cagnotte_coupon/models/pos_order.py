# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_account_move_line_product_key(self, values):
        product_key = super(PosOrder, self).\
            _get_account_move_line_product_key(values)
        account_cagnotte_id = values.get('account_cagnotte_id')
        if account_cagnotte_id:
            product_key += (values.get('account_cagnotte_id'), )
        return product_key

    @api.model
    def _payment_fields(self, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(ui_paymentline)
        res['account_cagnotte_id'] = ui_paymentline.get('account_cagnotte_id')
        return res

    @api.multi
    def _prepare_statement_line_payment_values(self, data):
        values = super(PosOrder, self).\
            _prepare_statement_line_payment_values(data)
        values['account_cagnotte_id'] = data.get('account_cagnotte_id')
        return values

    @api.model
    def _prepare_product_account_move_line(self, line, partner_id, account_id):
        values = super(PosOrder, self)._prepare_product_account_move_line(
            line, partner_id, account_id)
        if not values.get('account_cagnotte_id'):
            values['account_cagnotte_id'] = getattr(
                line.account_cagnotte_id, 'id', False)
        return values
