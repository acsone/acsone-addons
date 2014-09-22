# -*- coding: utf-8 -*-
#
###############################################################################
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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
###############################################################################
from uuid import uuid4
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.addons.mass_mailing_distribution_list.mass_mailing import \
    MSG_OK, MSG_KO


class test_mass_mailing(SharedSetupTransactionCase):

    def setUp(self):
        super(test_mass_mailing, self).setUp()

        self.distri_list_obj = self.registry['distribution.list']
        self.ml_obj = self.registry['mail.mass_mailing']
        self.distri_list_line_obj = self.registry['distribution.list.line']
        self.partner_obj = self.registry['res.partner']

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_try_unsubscribe_url(self):
        cr, uid, context = self.cr, self.uid, {}
        vals = {
            'name': '%s' % uuid4(),
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)
        partner_model = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]
        vals = {
            'name': '%s' % uuid4(),
            'src_model_id': partner_model,
            'domain': "[('id', 'in', [%s])]" % (p_id),
        }
        dll_id = self.distri_list_line_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': partner_model,
            'newsletter': False,
            'to_include_distribution_list_line_ids': [(4, dll_id)]
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)
        vals = {
            'name': 'Test',
            'contact_ab_pc': 100,
            'mailing_model': 'res.partner',
            'state': 'draft',
            'reply_to_mode': 'email',
            'reply_to': 'Test <test@example.com>',
            'distribution_list_id': dl_id,
            'email_from': 'Test <test@test.com>'
        }
        mailing_id = self.ml_obj.create(cr, uid, vals, context=context)
        msg = self.ml_obj.try_update_opt(
            cr, uid, mailing_id, p_id, context=context)
        self.assertEquals(msg, MSG_OK,
                          'Should be unsubscribe')
        msg = self.ml_obj.try_update_opt(
            cr, uid, -1, p_id, context=context)
        self.assertEquals(msg, MSG_KO,
                          'Should not be unsubscribe')
