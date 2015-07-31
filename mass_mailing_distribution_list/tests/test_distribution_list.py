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

from openerp.osv import orm


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

        irp_ids = self.ir_cfg_obj.search(
            self.cr, self.uid, [('key', '=', 'mail.catchall.domain')])

        if not irp_ids:
            # create the domain alias to avoid exception during the creation
            # of the distribution list alias
            vals = {
                'key': 'mail.catchall.domain',
                'value': 'test.eu',
            }
            self.ir_cfg_obj.create(self.cr, self.uid, vals)

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
        self.assertRaises(
            orm.except_orm, self.distri_list_obj.write,
            cr, uid, dl_id, vals, context=context)

        vals = {
            'mail_forwarding': True,
            'alias_name': 'xyz',
        }
        self.distri_list_obj.write(
            cr, uid, dl_id, vals, context=context)
        self.assertTrue(
            self.distri_list_obj.allow_forwarding(
                cr, uid, dl_id, context=context),
            'Should be allowed to make mail forwarding')

        vals = {
            'mail_forwarding': False,
        }
        self.distri_list_obj.write(
            cr, uid, dl_id, vals, context=context)
        self.assertFalse(
            self.distri_list_obj.allow_forwarding(
                cr, uid, dl_id, context=context),
            'Mail forwarding should be not allowed')

    def test_alias_name(self):
        cr, uid, context = self.cr, self.uid, {}

        catchall = 'demo'
        dl_name = '%s' % uuid4()

        # disable temporary the catchall alias
        catchall_id = self.ir_cfg_obj.search(
            cr, uid, [('key', '=', 'mail.catchall.alias')], context=context)
        self.ir_cfg_obj.write(
            cr, uid, catchall_id,
            {'key': 'tmp.mail.catchall.alias'}, context=context)

        # now this must raise
        self.assertRaises(
            orm.except_orm, self.distri_list_obj._build_alias_name,
            cr, uid, dl_name, context=context)

        # re-enable the catchall alias
        self.ir_cfg_obj.write(
            cr, uid, catchall_id,
            {'key': 'mail.catchall.alias', 'value': catchall}, context=context)

        # now this must produce an alias without exception
        alias_name = self.distri_list_obj._build_alias_name(
            cr, uid, dl_name, context=context)
        self.assertEqual(
            alias_name, '%s+%s' % (catchall, dl_name),
            'Generated alias name should be "catchall+dl_name"')

        vals = {
            'name': dl_name,
            'dst_model_id': self.partner_model,
            'alias_name': alias_name,
        }
        dl_id = self.distri_list_obj.create(cr, uid, vals, context=context)
        dl = self.distri_list_obj.browse(cr, uid, dl_id, context=context)

        self.assertFalse(
            dl.alias_name,
            'Without mail forwarding, alias name should be null')

        vals = {
            'mail_forwarding': True,
            'alias_name': alias_name,
        }
        self.distri_list_obj.write(cr, uid, dl_id, vals, context=context)

        self.assertEqual(
            dl.alias_name, alias_name,
            'Without mail forwarding, alias name should be "catchall+dl_name"')

        self.assertTrue(
            eval(dl.alias_defaults).get('distribution_list_id', False),
            'Default value should be a dictionary with the key '
            '"distribution_list_id"')
        alias_dl_id = eval(dl.alias_defaults)['distribution_list_id']
        self.assertEquals(
            alias_dl_id, dl_id,
            'Distribution list ID and '
            'alias distribution list ID should be the same')
        distribution_list_model_id = self.registry['ir.model'].search(
            cr, uid, [('model', '=', 'distribution.list')])[0]
        self.assertEqual(
            dl.alias_model_id.id, distribution_list_model_id,
            'Alias model should be "distribution list"')

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
            'mail_forwarding': True,
            'alias_name': self.distri_list_obj._build_alias_name(
                cr, uid, dl_name, context=context),
        }
        self.distri_list_obj.write(cr, uid, dl_id, vals, context=context)
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
        vals = {
            'name': name,
            'email': email_from,
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)

        partner_ids = self.distri_list_obj._get_mailing_object(
            cr, uid, dl_id, '<%s>' % email_from, context=context)
        self.assertEqual(p_id, partner_ids and partner_ids[0],
                         'Partner should be the same')

        partner_ids = self.distri_list_obj._get_mailing_object(
            cr, uid, dl_id, '<%s>' % email_from,
            mailing_model='res.partner', context=context)
        self.assertEqual(p_id, partner_ids and partner_ids[0],
                         'Partner should be the same')
