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
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase


class test_distribution_list(SharedSetupTransactionCase):

    def setUp(self):
        super(test_distribution_list, self).setUp()

        self.distri_list_obj = self.registry['distribution.list']
        self.distri_list_line_obj = self.registry['distribution.list.line']
        self.alias_obj = self.registry['mail.alias']
        self.partner_obj = self.registry['res.partner']
        self.ir_cfg_obj = self.registry['ir.config_parameter']
        self.mail_obj = self.registry['mail.mail']

        self.partner_model = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_update_opt(self):
        '''
        Check
        * update opt with out/in/wrong value
        * length of opt_(out/in)_ids after update
        '''
        cr, uid, context = self.cr, self.uid, {}
        vals = {
            'name': '%s' % uuid4(),
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)
        vals['name'] = '%s' % uuid4(),
        p2_id = self.partner_obj.create(cr, uid, vals, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'src_model_id': self.partner_model,
            'domain': "[('id', 'in', [%s])]" % (p_id),
        }
        dll_id = self.distri_list_line_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': self.partner_model,
            'newsletter': True,
            'to_include_distribution_list_line_ids': [(4, dll_id)]
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)

        # opt in
        self.distri_list_obj.update_opt(
            cr, uid, dl_id, [p2_id], mode='in', context=context)
        dl = self.distri_list_obj.browse(cr, uid, dl_id, context=context)
        self.assertTrue(len(dl.opt_in_ids) == 1, 'Should have one opt_in_ids')

        # remove 2 ids with opt_out
        self.distri_list_obj.update_opt(
            cr, uid, dl_id, [p_id, p2_id], mode='out', context=context)
        dl = self.distri_list_obj.browse(cr, uid, dl_id, context=context)
        self.assertTrue(len(dl.opt_out_ids) == 2,
                        'Should have two opt_out_ids')

        self.assertRaises(orm.except_orm, self.distri_list_obj.update_opt, cr,
                          uid, dl_id, [p_id], mode='bad', context=context)

    def test_get_ids_from_distribution_list(self):
        '''
        manage opt in/out.
        Check that
        * opt_in ids are into the res_ids
        * opt_out ids are not into the res_ids
        '''
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
            'domain': "[('id', '=', %s)]" % p_id,
        }
        dll_id = self.distri_list_line_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': partner_model,
            'newsletter': True,
            'to_include_distribution_list_line_ids': [(4, dll_id)]
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)
        res_ids = self.distri_list_obj.get_ids_from_distribution_list(
            cr, uid, [dl_id], context=context)
        self.assertTrue(len(res_ids) == 1,
                        'Should have one partner into res_ids')
        # remove this partner with excluded filter
        vals = {
            'to_exclude_distribution_list_line_ids': [(4, dll_id)]
        }
        self.distri_list_obj.write(
            cr, uid, [dl_id], vals, context=context)
        res_ids = self.distri_list_obj.get_ids_from_distribution_list(
            cr, uid, [dl_id], context=context)
        self.assertFalse(res_ids, 'Should have an empty res_ids')
        # now add it into opt_in_ids
        self.distri_list_obj.update_opt(
            cr, uid, dl_id, [p_id], mode='in', context=context)
        res_ids = self.distri_list_obj.get_ids_from_distribution_list(
            cr, uid, [dl_id], context=context)
        self.assertTrue(len(res_ids) == 1, 'Should have one partner into '
                        'res_ids cause of opt_in_ids')
        # now add it into opt_out_ids
        self.distri_list_obj.update_opt(
            cr, uid, dl_id, [p_id], mode='out', context=context)
        res_ids = self.distri_list_obj.get_ids_from_distribution_list(
            cr, uid, [dl_id], context=context)
        self.assertFalse(res_ids, 'Should have an empty res_ids')

    def test_allow_forwarding(self):

        cr, uid, context = self.cr, self.uid, {}

        # create the domain alias to avoid exception during the creation
        # of the distribution list alias
        vals = {
            'key': 'mail.catchall.domain',
            'value': 'test.eu',
        }
        self.ir_cfg_obj.create(cr, uid, vals, context=context)

        vals = {
            'name': '%s' % uuid4(),
            'dst_model_id': self.partner_model,
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)

        self.assertFalse(
            self.distri_list_obj.allow_forwarding(
                cr, uid, dl_id, context=context),
            'Should not be allowed to make mail forwarding')

        vals = {
            'mail_forwarding': True,
        }
        self.distri_list_obj.write(
            cr, uid, dl_id, vals, context=context)

        self.assertTrue(
            self.distri_list_obj.allow_forwarding(
                cr, uid, dl_id, context=context),
            'Should be allowed to make mail forwarding')
        dl_values = self.distri_list_obj.read(
            cr, uid, dl_id, ['mail_alias_id'], context=context)

        self.assertTrue(
            dl_values.get('mail_alias_id', False),
            'A mail alias should be generated')
        vals = {
            'mail_forwarding': False,
        }
        self.distri_list_obj.write(
            cr, uid, dl_id, vals, context=context)
        self.assertTrue(
            dl_values.get('mail_alias_id', False),
            'Mail alias should not be reset after being generated')

    def test_generate_alias(self):
        cr, uid, context = self.cr, self.uid, {}
        dl_name = '%s' % uuid4()
        vals = {
            'name': dl_name,
            'dst_model_id': self.partner_model,
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)

        # unlink to force raise
        alias_id = self.ir_cfg_obj.search(
            cr, uid, [('key', '=', 'mail.catchall.alias')], context=context)
        self.ir_cfg_obj.unlink(cr, uid, alias_id, context=context)

        # will fail if no alias into ir.parameter
        self.assertRaises(orm.except_orm, self.distri_list_obj.generate_alias,
                          cr, uid, dl_id, dl_name, context=context)

        # create the domain alias to avoid exception during the creation
        # of the distribution list alias
        alias = 'demo'
        vals = {
            'key': 'mail.catchall.alias',
            'value': alias,
        }
        alias_id = self.ir_cfg_obj.create(cr, uid, vals, context=context)

        alias_id = self.distri_list_obj.generate_alias(
            cr, uid, dl_id, dl_name, context=context)
        alias_values = self.alias_obj.read(
            cr, uid, alias_id,
            ['alias_name', 'alias_defaults', 'alias_model_id'],
            context=context)
        self.assertEqual(alias_values['alias_name'], '%s+%s'
                         % (alias, dl_name),
                         'Generated name should be "alias+dl_name"')
        self.assertTrue(eval(alias_values['alias_defaults']).
                        get('distribution_list_id', False),
                        'Default value should be a dict that contains key '
                        '"distribution_list_id"')
        alias_dl_id =\
            eval(alias_values['alias_defaults'])['distribution_list_id']
        self.assertEquals(alias_dl_id, dl_id,
                          'Distribution list ID and alias distribution List '
                          'ID should be the same')
        distribution_list_model_id = self.registry['ir.model'].search(
            cr, uid, [('model', '=', 'distribution.list')])[0]
        self.assertEqual(alias_values['alias_model_id'][0],
                         distribution_list_model_id,
                         'Alias model should be distribution list alias')

    def test_message_new(self):
        cr, uid, context = self.cr, self.uid, {}
        msg_dict = {}
        dl_id = self.distri_list_obj.message_new(
            cr, uid, msg_dict, custom_values=None, context=context)
        self.assertEqual(dl_id, None,
                         'Should not succeed without "custom_values"')
        dl_id = self.distri_list_obj.message_new(
            cr, uid, msg_dict, custom_values={}, context=context)
        self.assertEqual(dl_id, None,
                         'Should not succeed without a "distribution_list_id" '
                         'into "custom_values"')
        dl_name = '%s' % uuid4()
        vals = {
            'name': dl_name,
            'dst_model_id': self.partner_model,
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)
        custom_values = {
            'distribution_list_id': dl_id,
        }
        attended_dl_id = self.distri_list_obj.message_new(
            cr, uid, msg_dict, custom_values=custom_values, context=context)
        self.assertEqual(dl_id, attended_dl_id,
                         'Concerned distribution list should be the same '
                         'as the passed present one into "custom_values"')
        vals = {
            'key': 'mail.catchall.domain',
            'value': 'test.eu',
        }
        self.ir_cfg_obj.create(cr, uid, vals, context=context)
        vals = {
            'mail_forwarding': True,
        }
        self.distri_list_obj.write(
            cr, uid, dl_id, vals, context=context)
        msg_dict['email_from'] = "<test@test.be>"
        msg_dict['subject'] = 'test'
        msg_dict['body'] = 'body'
        msg_dict['attachments'] = [('filename', 'content')]
        attended_dl_id = self.distri_list_obj.message_new(
            cr, uid, msg_dict, custom_values=custom_values, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'email': 'test@test.be',
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)
        self.distri_list_obj.message_new(
            cr, uid, msg_dict, custom_values=custom_values, context=context)
        mail_ids = self.mail_obj.search(
            cr, uid, [('res_id', '=', p_id), ('model', '=', 'res.partner')],
            context=context)
        self.assertTrue(mail_ids, 'A mail should have been created to this '
                        'partner')
        mail_values = self.mail_obj.read(
            cr, uid, mail_ids[0], ['attachment_ids'], context=context)
        self.assertTrue(mail_values.get('attachment_ids', False),
                        'Mail Should have an attachment')

    def test_get_mailing_object(self):
        cr, uid, context = self.cr, self.uid, {}
        name = '%s' % uuid4()
        email_from = '%s@test.eu' % uuid4()
        vals = {
            'name': name,
            'dst_model_id': self.partner_model,
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)

        # partner
        vals = {
            'name': 'parent-%s' % name,
            'email': 'parent-%s' % email_from,
        }
        parent_id = self.partner_obj.create(cr, uid, vals, context=context)
        vals = {
            'name': name,
            'email': email_from,
            'parent_id': parent_id,
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)

        partner_id = self.distri_list_obj._get_mailing_object(
            cr, uid, dl_id, '<%s>' % email_from, context=context)
        self.assertEqual(p_id, partner_id,
                         'Partner should be the same')

        # parent id is a res.partner should have the same result
        partner_id = self.distri_list_obj._get_mailing_object(
            cr, uid, dl_id, '<parent-%s>' % email_from,
            sublevel_id='parent_id', context=context)
        self.assertEqual(parent_id, partner_id,
                         'Partner should be the same')
