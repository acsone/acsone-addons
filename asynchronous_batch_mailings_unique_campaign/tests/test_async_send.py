# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from uuid import uuid4

ADMIN_USER_ID = common.ADMIN_USER_ID


class TestAsynBatchMailingUniqueCampaign(common.TransactionCase):

    def setUp(self):
        super(TestAsynBatchMailingUniqueCampaign, self).setUp()
        self.mail_compose_message_model = self.env['mail.compose.message']

    def test_async_send_mail(self):
        name = uuid4()
        mail_composer_vals = {
            'email_from': 'test@test.be',
            'composition_mode': 'mass_mail',
            'partner_ids': [[6, False, []]],
            'subject': 'test',
            'mass_mailing_name': name,
            'model': 'res.partner'
        }
        self.mail_compose_message_model._prepare_vals(mail_composer_vals)
        self.assertFalse(
            mail_composer_vals.get('mass_mailing_name'),
            'Should not have a mass_mailing name')
        self.assertTrue(
            mail_composer_vals.get('mass_mailing_id'),
            'Should not have a mass_mailing ID instead')
