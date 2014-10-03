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
from openerp.tests import common


class test_event(common.TransactionCase):

    def setUp(self):
        super(test_event, self).setUp()

        self.ee_obj = self.env['event.event']
        self.er_obj = self.env['event.registration']
        self.mm_obj = self.env['mail.mass_mailing']
        self.et_obj = self.env['email.template']
        self.p_obj = self.env['res.partner']
        self.mms = self.env['mail.mail.statistics']

    def test_check_registrations(self):
        '''
        * event.event: registrations consistency with event action
        * event.registration: do not allow to confirm registration if the event
        has no template `email_registration_id`
        '''
        vals = {
            'name': 'My Event',
            'date_begin': '2014-10-29 14:57:08',
            'date_end': '2014-10-29 15:57:08',
        }
        event_id = self.ee_obj.create(vals)
        vals = {
            'name': 'Bill',
            'email': 'bill@exemple.fr',
        }
        p_id = self.p_obj.create(vals)
        vals = {
            'event_id': event_id.id,
            'partner_id': p_id.id,
            'name': p_id.name,
            'email': p_id.email,
        }
        all_states = [c[0] for c in self.er_obj._columns['state'].selection]
        self.assertRaises(Exception, event_id._check_registrations, all_states)
        reg_ids = self.er_obj.create(vals)
        # this should
        self.assertTrue(event_id._check_registrations(all_states),
                        'Should have registrations')
        self.assertRaises(Exception, reg_ids.registration_open)

    def test_mass_mailing_action(self):
        '''
        Test create/update depending of a template and event
        '''
        er_model = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'event.registration')])[0],
        vals = {
            'name': 'Invitation of the Event',
            'subject': 'Your Invitation at ${object.event_id.name}',
            'model_id': er_model,
            'body_html': 'Invitation',
            'email_to': '${object.email|safe}',
            'email_from': 'sample@exemple.fr',
        }
        invitation_template_id = self.et_obj.create(vals)
        vals = {
            'name': 'Confirmation of the Event',
            'subject': 'Your Confirmation at ${object.event_id.name}',
        }
        confirmation_template_id = invitation_template_id.copy(default=vals)
        vals = {
            'name': 'Cancellation of the Event',
            'subject': 'Your Cancellation at ${object.event_id.name}',
        }
        cancellation_template_id = invitation_template_id.copy(default=vals)
        vals = {
            'name': 'My Event',
            'email_registration_id': confirmation_template_id.id,
            'email_confirmation_id': confirmation_template_id.id,
            'cancellation_template_id': cancellation_template_id.id,
            'invitation_template_id': invitation_template_id.id,
            'date_begin': '2014-10-29 14:57:08',
            'date_end': '2014-10-29 15:57:08',
        }
        event_id = self.ee_obj.create(vals)
        vals = {
            'name': 'Bill',
            'email': 'bill@exemple.fr',
        }
        p_id = self.p_obj.create(vals)
        vals = {
            'event_id': event_id.id,
            'partner_id': p_id.id,
            'name': p_id.name,
            'email': p_id.email,
        }
        reg_id = self.er_obj.create(vals)
        create, mailing = event_id._mass_mailing_action(
            invitation_template_id, event_id.invite_mass_mailing_id)
        self.assertTrue(create, 'Should Create The "invite_mass_mailing_id"')
        self.assertEqual(mailing.name, invitation_template_id.subject,
                         'Mailing "name" Should Have Same Values Than '
                         'Template "subject"')
        self.assertTrue(invitation_template_id.body_html in mailing.body_html,
                        'Mailing "body_html" Should Have Same Values Than '
                        'Template "body_html"')
        self.assertEqual(mailing.email_from, invitation_template_id.email_from,
                         'Mailing "email_from" Should Have Same Values Than '
                         'Template "email_from"')
        state_id = self.mms.search([('mass_mailing_id', '=', mailing.id)])
        self.assertTrue(state_id, 'Should have a statistic with this mailing')

        event_id.button_send_invitation()
        self.assertTrue(event_id.invite_mass_mailing_id,
                        'Should Have a Mass Mailing For Invitations')
        self.assertTrue(event_id.invitation_date,
                        'Should Have a Invitation Sent Date')
        reg_id.confirm_registration()
        event_id.confirm_event()
        self.assertTrue(event_id.confirm_mass_mailing_id,
                        'Should Have a Mass Mailing For Confirmations')
        self.assertTrue(event_id.confirmation_date,
                        'Should Have a Confirmation Sent Date')
        event_id.button_cancel()
        self.assertTrue(event_id.cancel_mass_mailing_id,
                        'Should Have a Mass Mailing For Cancellation')
        self.assertTrue(event_id.cancellation_date,
                        'Should Have a Cancellation Sent Date')
