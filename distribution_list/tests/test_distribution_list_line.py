# -*- coding: utf-8 -*-
##############################################################################
#
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
#
##############################################################################
from uuid import uuid4
import openerp.tests.common as common


class test_distribution_list_line(common.TransactionCase):

    def setUp(self):
        super(test_distribution_list_line, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.dll_obj = self.registry('distribution.list.line')

    def test_write(self):
        """
        ==========
        test_write
        ==========
        Check that:
        * changing only `src_model_id` will reset `domain` with `[]`
        * changing both will act like a native orm `write`
        """
        cr, uid, context = self.cr, self.uid, {}
        model_obj = self.registry('ir.model')
        partner_model_id = model_obj.search(
            cr, uid, [('model', '=', 'email.template')], context=context)[0]
        email_template_model_id = model_obj.search(
            cr, uid, [('model', '=', 'email.template')], context=context)[0]
        domain = "[('is_company', '=', False)]"

        dll_values = {
            'name': '%s' % uuid4(),
            'src_model_id': partner_model_id,
            'domain': domain
        }

        dll_id = self.dll_obj.create(cr, uid, dll_values, context=context)
        dll = self.dll_obj.browse(cr, uid, dll_id, context=context)
        self.assertEqual(dll.domain, domain, "Domains should be the same")

        # only change the src_model_id
        self.dll_obj.write(
            cr, uid, dll_id, {'src_model_id': email_template_model_id},
            context=context)
        dll = self.dll_obj.browse(cr, uid, dll_id, context=context)
        self.assertEqual(dll.domain, '[]',
                         "Domain should be the default value")

        # change src_model_id and domain
        dll_values.pop('name')
        self.dll_obj.write(cr, uid, dll_id, dll_values, context=context)
        dll = self.dll_obj.browse(cr, uid, dll_id, context=context)
        self.assertEqual(dll.domain, domain, "Domains should be the same")

    def test_action_partner_selection(self):
        """
        =============================
        test_action_partner_selection
        =============================
        Verify that the dictionary returned has well:
        * same model than the distribution list line
        * a `flags` with {'search_view': True}
        """
        cr, uid, context = self.cr, self.uid, {}
        model_obj = self.registry('ir.model')
        partner_model_id = model_obj.search(
            cr, uid, [('model', '=', 'email.template')], context=context)[0]
        domain = "[('is_company', '=', False)]"

        dll_values = {
            'name': '%s' % uuid4(),
            'src_model_id': partner_model_id,
            'domain': domain
        }

        dll_id = self.dll_obj.create(cr, uid, dll_values, context=context)
        dll = self.dll_obj.browse(cr, uid, dll_id, context=context)
        res_dict = self.dll_obj.action_partner_selection(cr, uid, [dll_id],
                                                         context=context)
        self.assertEqual(dll.src_model_id.model, res_dict['res_model'],
                         "Model should be the same")
        self.assertTrue(res_dict['flags']['search_view'],
                        "Should have a search view to be able to select\
                        a domain")
