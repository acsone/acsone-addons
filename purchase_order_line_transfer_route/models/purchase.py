# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors:  Adrien Peiffer - Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(
            self, order, order_line, picking_id, group_id):
        """
        Manage another route if line has a transfer_route_id
        """
        res = super(PurchaseOrder, self).\
            _prepare_order_line_move(order, order_line, picking_id, group_id)
        for partial_res in res:
            if order_line.transfer_route_id.id:
                partial_res['route_ids'].append(
                    (4, order_line.transfer_route_id.id))
        return res


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    transfer_route_id = fields.Many2one(
        comodel_name='stock.location.route', string='Transfer Route')
