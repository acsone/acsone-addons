# -*- coding: utf-8 -*-
#
#
#    Authors: Stéphane Bidoul & Laetitia Gangloff
#    Contributors: Muschang Anthony
#    Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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
#
from openerp.osv import osv, fields


class event_multiple_registration(osv.osv_memory):
    _name = 'event.multiple.registration'
    _description = 'Event multiple registration'

    _columns = {
        "partner_ids": fields.many2many('res.partner', string="Partners"),
    }

    def button_add(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        event_pool = self.pool.get('event.event')
        event_pool.add_multiple_partner(cr, uid, context['active_ids'][0], wizard.partner_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

