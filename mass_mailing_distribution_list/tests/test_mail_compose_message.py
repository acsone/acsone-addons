# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mass_mailing_distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mass_mailing_distribution_list is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mass_mailing_distribution_list is distributed
#     in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mass_mailing_distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from uuid import uuid4
from anybox.testing.openerp import SharedSetupTransactionCase

SRC_MODEL = 'res.partner'


class TestMailComposeMessage(SharedSetupTransactionCase):

    def setUp(self):
        super(TestMailComposeMessage, self).setUp()

        self.distri_list_obj = self.registry['distribution.list']
        self.mass_mailing_obj = self.registry['mail.mass_mailing']
        self.mail_compose_message_obj = self.registry['mail.compose.message']
        self.dst_model_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', SRC_MODEL)], limit=1)[0]

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_create_mail_compose_message(self):
        """
        If a `mail.compose.message` is create with a `mail.mass_mailing`
        that has a `distribution_list_id` then the `mail.compose.message`
        should have this `distribution_list_id` too
        """
        cr, uid, context = self.cr, self.uid, {}

        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': self.dst_model_id,
        }
        distribution_list_id = self.distri_list_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': 'test',
            'reply_to_mode': 'email',
            'distribution_list_id': distribution_list_id,
        }
        mass_mailing_id = self.mass_mailing_obj.create(cr, uid, vals,
                                                       context=context)
        vals = {
            'subject': 'test',
            'model': 'res.partner',
            'email_from': 'test@test.tst',
            'record_name': False,
            'composition_mode': 'mass_mail',
            'mass_mailing_id': mass_mailing_id,
            'no_auto_thread': True,
        }
        mail_compose_message_id = self.mail_compose_message_obj.create(
            cr, uid, vals, context=context)
        mail_compose_message_rec = self.mail_compose_message_obj.\
            browse(cr, uid, mail_compose_message_id, context=context)
        self.assertEqual(mail_compose_message_rec.distribution_list_id and
                         mail_compose_message_rec.distribution_list_id.id,
                         distribution_list_id, 'Wizard should have the same \
                         distribution list than its mass_mailing')

    def test_get_mail_values(self):
        """
        If a `mail.compose.message` has a `distribution_list_id` and a
        `mail.mass_mailing` then this `mail.mass_mailing` should have the same
        `distribution_list_id`
        """
        cr, uid, context = self.cr, self.uid, {}
        # distribution list
        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': self.dst_model_id,
        }
        distribution_list_id = self.distri_list_obj.create(
            cr, uid, vals, context=context)

        # mail compose message
        mass_mailing_name = '%s' % uuid4()
        vals = {
            'model': SRC_MODEL,
            'email_from': 'test@test.tst',
            'record_name': False,
            'composition_mode': 'mass_mail',
            'distribution_list_id': distribution_list_id,
            'mass_mailing_name': mass_mailing_name,
            'subject': 'New Gadgets',
            'no_auto_thread': True,
        }
        mail_compose_message_id = self.mail_compose_message_obj.create(
            cr, uid, vals, context=context)
        self.mail_compose_message_obj.send_mail(
            cr, uid, [mail_compose_message_id], context=context)

        mass_mailing_ids = self.mass_mailing_obj.search(
            cr, uid, [('name', '=', mass_mailing_name)], context=context)
        self.assertTrue(mass_mailing_ids, 'Should have a mass_mailing with \
            the name %s' % mass_mailing_name)
        mass_mailing_rec = self.mass_mailing_obj.browse(
            cr, uid, mass_mailing_ids[0], context=context)
        self.assertEquals(mass_mailing_rec.distribution_list_id and
                          mass_mailing_rec.distribution_list_id.id,
                          distribution_list_id, 'Should have a mass_mailing \
                          with the name %s' % mass_mailing_name)
