# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Muschang Anthony
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
##############################################################################
from openerp.osv import orm


class event_event(orm.Model):
    _inherit = 'event.event'

    def add_multiple_partner(self, cr, uid, id_, partner_ids_to_add, context=None):
        """
            Add multiple partner and avoid making duplicate entry
        """

        if len(partner_ids_to_add) == 0:
            return

        event_id = id_
        partner_ids = [partner.id for partner in partner_ids_to_add]
        # code optimization: use a SQL Select to retrieve the list of partner_id
        # already registered for the event. By by passing the orm, we avoid the
        # default get_name made by the orm when retrieving a relation.
        cr.execute("""
            select
                partner_id
            from
                event_registration
            where
                event_id = %s
            and
                partner_id in %s
        """, (event_id, tuple(partner_ids)))
        # Reload the list of ids found by the search using the ORM to apply the security constrains to
        # the search result
        registered_partner_ids = [partner[0] for partner in cr.fetchall()]

        registered_partner_ids = self.pool.get("res.partner").read(cr, uid, registered_partner_ids, ['id'])
        registered_partner_ids = [res.get('id') for res in registered_partner_ids]

        att_data = [{'partner_id': att.id,
                     'email': att.email,
                     'name': att.name,
                     'phone': att.phone,
                     } for att in partner_ids_to_add if att.id not in registered_partner_ids]

        self.pool.get('event.event').write(cr, uid, event_id,
                                           {'registration_ids': [(0, 0, data) for data in att_data]},
                                               context)
