# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerToNotify(TransactionCase):

    def setUp(self):
        super(TestPartnerToNotify, self).setUp()
        self.BusObj = self.env['bus.bus']
        self.MailObj = self.env['mail.mail']
        self.MailMessageObj = self.env['mail.message'].with_context(
            mail_auto_delete=False)
        self.PartnerObj = self.env['res.partner']

        self.partner1 = self.create_partner('1')
        self.partner2 = self.create_partner('2')
        self.partner3 = self.create_partner('3')
        self.partner4 = self.create_partner('4')
        self.partner5 = self.create_partner('5')

    def create_partner(self, suffix):
        return self.PartnerObj.create({
            'name': 'partner-%s' % suffix,
            'email': 'partner-%s@test.com' % suffix,
            'notify_email': 'always',
        })

    def create_message(self, message_record, partner_ids, to_notify=None):
        MailMessageObj = self.MailMessageObj
        if to_notify:
            MailMessageObj = MailMessageObj.with_context(
                partners_to_notify=to_notify)

        return MailMessageObj.create({
            'subject': 'Testing',
            'body': "Test message",
            'email_from': "admin@test.com",
            'partner_ids': [(6, 0, partner_ids)],
            'model': message_record._name,
            'res_id': message_record.id,
        })

    def test_01_partner_to_notify(self):
        partner_ids = [self.partner2.id, self.partner3.id]
        partner_ids_to_notify = [self.partner4.id, self.partner5.id]

        message = self.create_message(self.partner1, partner_ids)
        self.assertEquals(message.partner_ids.ids, partner_ids)

        mail = self.MailObj.search([
            ('message_id', '=', message.message_id),
        ])
        self.assertEquals(len(mail), 1)
        self.assertEquals(mail.recipient_ids.ids, partner_ids)

        message2 = self.create_message(
            self.partner1, partner_ids, to_notify=partner_ids_to_notify)
        self.assertEquals(
            message2.partner_ids.ids,
            partner_ids + partner_ids_to_notify)

        mail = self.MailObj.search([
            ('message_id', '=', message2.message_id),
        ])
        self.assertEquals(len(mail), 1)
        self.assertEquals(mail.recipient_ids.ids, partner_ids_to_notify)
