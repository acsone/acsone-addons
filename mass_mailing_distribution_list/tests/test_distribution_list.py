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
        self.partner_obj = self.registry['res.partner']

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_update_opt(self):
        '''
        Check
        * update opt with out/in/wrong value
        * length of opt_(out/in)_ids after update
        '''
        cr, uid, context = self.cr, self.uid, {}
        partner_model = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]
        vals = {
            'name': '%s' % uuid4(),
        }
        p_id = self.partner_obj.create(cr, uid, vals, context=context)
        vals['name'] = '%s' % uuid4(),
        p2_id = self.partner_obj.create(cr, uid, vals, context=context)
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
