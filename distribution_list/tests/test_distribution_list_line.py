# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     distribution_list is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     distribution_list is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from uuid import uuid4

import openerp.tests.common as common

SUPERUSER_ID = common.ADMIN_USER_ID


class TestDistributionListLine(common.TransactionCase):

    def setUp(self):
        super(TestDistributionListLine, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.dll_obj = self.registry('distribution.list.line')

    def test_write(self):
        """
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

    def test_get_list_from_domain(self):
        """
        Test that action is well returned with correct value required for
        a `get_list_from_domain`
        """
        cr, uid, context = self.cr, self.uid, {}
        distribution_list_line_obj = self.registry['distribution.list.line']
        partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        dl_name = '%s' % uuid4()

        distribution_list_line_id = distribution_list_line_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'domain': "[['name', '=', '%s']]" % dl_name,
                'src_model_id': partner_model_id,
            })
        vals = distribution_list_line_obj.get_list_from_domain(
            cr, uid, distribution_list_line_id, context=context)

        self.assertEqual(vals['type'], 'ir.actions.act_window',
                         "Should be an ir.actions.act_window ")
        self.assertEqual(vals['res_model'], 'res.partner',
                         "Model should be the same than the distribution list")
