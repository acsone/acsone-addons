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

import openerp.tests.common as common
import logging
import datetime

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_add_partners(common.TransactionCase):

    def test_duplicate(self):
        """
            Test adding duplicate partners in an event
        """

        partner_model = self.registry('res.partner')
        event_model = self.registry('event.event')

        user_id = self.ref("base.user_demo")

        #CREATE three partners
        partners_ids = []
        partners_ids.append(partner_model.create(self.cr, user_id, {
            'name': 'John',
        }))

        partners_ids.append(partner_model.create(self.cr, user_id, {
            'name': 'Jack',
        }))

        partners_ids.append(partner_model.create(self.cr, user_id, {
            'name': 'Carl',
        }))

        #CREATE an event
        event_id = event_model.create(self.cr, user_id, {
            'name': 'test event',
            'date_begin': datetime.date(2013, 01, 01),
            'date_end': datetime.date(2013, 02, 01),
        })

        #Add the partners in the event
        partners = partner_model.browse(self.cr, self.uid, partners_ids)
        event_model.add_multiple_partner(self.cr, user_id, event_id, partners)

        event = event_model.browse(self.cr, self.uid, event_id)
        self._check_partner_with_partner_in_event_registration(partners_ids, event)

        #Add the partners in the event again
        event_model.add_multiple_partner(self.cr, user_id, event_id, partners)

        event = event_model.browse(self.cr, self.uid, event_id)
        self._check_partner_with_partner_in_event_registration(partners_ids, event)

        #Add the partners with a new one in the event again
        partners_ids.append(partner_model.create(self.cr, user_id, {
            'name': 'Bob',
        }))
        partners = partner_model.browse(self.cr, self.uid, partners_ids)
        event_model.add_multiple_partner(self.cr, user_id, event_id, partners)

        event = event_model.browse(self.cr, self.uid, event_id)
        self._check_partner_with_partner_in_event_registration(partners_ids, event)

        #Add 0 partners
        event_model.add_multiple_partner(self.cr, user_id, event_id, [])
        event = event_model.browse(self.cr, self.uid, event_id)
        self._check_partner_with_partner_in_event_registration(partners_ids, event)

    def _check_partner_with_partner_in_event_registration(self, partners_ids, event):
        self.assertEqual(len(event.registration_ids), len(partners_ids),
                         "The registration count should be the same as the number of partners added")

        partners_in_registration = []
        i = 0
        while i < len(partners_ids):
            partners_in_registration.append(event.registration_ids[i].partner_id.id)
            i += 1

        self.assertEqual(set(partners_in_registration), set(partners_ids),
                         "Each registration should correspond with the partners added")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
