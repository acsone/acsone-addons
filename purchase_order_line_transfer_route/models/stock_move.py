# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Adrien Peiffer - Nemry Jonathan
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
from openerp import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _push_apply(self, moves):
        """
        Redefined rules priority
        """
        push_obj = self.env['stock.location.path']
        for move in moves:
            route_ids = []
            for route in move.route_ids:
                if route.purchase_line_selectable:
                    route_ids.append(route.id)
            domain = [('location_from_id', '=', move.location_dest_id.id)]
            order = 'route_sequence,sequence'
            rules = push_obj.search(
                domain + [('route_id', 'in', route_ids)], order=order)
            if rules:
                push_obj._apply(rules, move)
            else:
                super(StockMove, self)._push_apply([move])
        return True
