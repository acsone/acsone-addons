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

from openerp.tools import SUPERUSER_ID


class TestMailMail(SharedSetupTransactionCase):

    def setUp(self):
        super(TestMailMail, self).setUp()

        self.distri_list_obj = self.registry['distribution.list']
        self.mail_mail_obj = self.registry['mail.mail']
        self.ml_obj = self.registry['mail.mass_mailing']
        self.distri_list_line_obj = self.registry['distribution.list.line']
        self.partner_obj = self.registry['res.partner']
        self.user_obj = self.registry['res.users']
        self.admin = self.ref('base.partner_root')

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_get_unsubscribe_url(self):
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
        vals = {
            'body': '<p>test</p>',
            'model': 'res.partner',
            'recipient_ids': [(4, self.admin)],
            'record_name': False,
            'attachment_ids': [],
            'mailing_id': mailing_id,
            'notification': True,
            'auto_delete': True,
            'body_html': '<p>test</p>',
            'no_auto_thread': False,
            'reply_to': 'Test <test@example.com>',
            'author_id': p_id,
            'res_id': p_id,
            'email_from': 'Test <test@example.com>',
            'subject': 'Test'
        }
        mail_id = self.mail_mail_obj.create(cr, uid, vals, context=context)
        mail = self.mail_mail_obj.browse(cr, uid, mail_id, context=context)
        url = self.mail_mail_obj._get_unsubscribe_url(
            cr, uid, mail, '', msg=None, context=None)
        self.assertTrue('/newsletter' not in url, 'Should have native url')
        vals = {
            'newsletter': True,
        }
        self.distri_list_obj.write(cr, uid, dl_id, vals, context=context)

        url = self.mail_mail_obj._get_unsubscribe_url(
            cr, uid, mail, '', msg=None, context=None)
        self.assertTrue('/newsletter' in url, 'Should have newsletter url')
        user_model = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.users')])[0]
        vals = {
            'partner_path': 'partner_id',
            'dst_model_id': user_model,
        }
        self.distri_list_obj.write(cr, uid, dl_id, vals, context=context)
        vals = {
            'model': 'res.users',
            'res_id': SUPERUSER_ID,
        }
        admin = self.user_obj.browse(cr, uid, SUPERUSER_ID, context=context)
        self.mail_mail_obj.write(cr, uid, mail_id, vals, context=context)
        mail = self.mail_mail_obj.browse(cr, uid, mail_id, context=context)
        url = self.mail_mail_obj._get_unsubscribe_url(
            cr, uid, mail, '', msg=None, context=None)
        self.assertTrue('res_id=%s' % admin.partner_id.id in url,
                        'Should have partner_id of'
                        'the user')
        vals = {
            'partner_path': 'wrong_value',
        }
        self.distri_list_obj.write(cr, uid, dl_id, vals, context=context)
        url = self.mail_mail_obj._get_unsubscribe_url(
            cr, uid, mail, '', msg=None, context=None)
        self.assertFalse(url, 'Should not have url due to bad partner_path')
