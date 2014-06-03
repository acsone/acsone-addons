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
from openerp import tools
from openerp.tools import convert_xml_import
import openerp.tests.common as common
import logging
import os
import collections

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
_logger = logging.getLogger(__name__)

DB = common.DB
SUPERUSER_ID = common.ADMIN_USER_ID


def get_file(module_name, fp):
    pathname = os.path.join(module_name, fp)
    return tools.file_open(pathname)


def load_data(cr, module_name, fp, idref=None, mode='init', noupdate=False, report=None):
    pathname = os.path.join(module_name, fp)
    fp = get_file(module_name, fp)
    _logger.info("Import datas from %s" % pathname)
    try:
        convert_xml_import(cr, module_name, fp, idref, mode, noupdate, report)
    except:
        _logger.info("%s already exists in database" % fp)
        pass


class test_confidentiality(common.TransactionCase):

    def setUp(self):
        super(test_confidentiality, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        load_data(self.cr, 'distribution_list', "tests/data/company_data.xml")
        load_data(self.cr, 'distribution_list', "tests/data/user_data.xml")

    def test_confidentiality_distribution_list(self):

        user_model = self.registry('res.users')
        distribution_list_model = self.registry('distribution.list')
        distribution_list_line_model = self.registry('distribution.list.line')

        user_id_1 = user_model.search(self.cr, self.uid, [('login', '=', 'first')])[0]
        user_id_2 = user_model.search(self.cr, self.uid, [('login', '=', 'second')])[0]
        user_creator = user_model.browse(self.cr, self.uid, user_id_1, context={})
        user_no_access = user_model.browse(self.cr, self.uid, user_id_2, context={})

        # create distribution_list_line and distribution_list with the first user
        id_distribution_list_line = distribution_list_line_model.create(self.cr, user_creator.id, {
            'name': 'employee',
            'domain': "[[\'employee\', \'=\', True]]",
            'src_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'company_id': user_creator.company_id.id,
        })
        _logger.info("%s create the distribution list line %s", user_creator.name, id_distribution_list_line)

        id_distribution_list = distribution_list_model.create(self.cr, user_creator.id, {
            'name': 'tee meeting',
            'company_id': user_creator.company_id.id,
            'dst_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'to_include_distribution_list_line_ids': [[4, id_distribution_list_line]],
        })
        _logger.info("%s create the distribution list %s", user_creator, id_distribution_list)

        ids = distribution_list_line_model.search(self.cr, user_creator.id, [('id', '=', id_distribution_list_line)])
        self.assertEqual(len(ids), 1, "User creator doesn't see its line")
        ids = distribution_list_line_model.search(self.cr, user_no_access.id, [('id', '=', id_distribution_list_line)])
        self.assertEqual(len(ids), 0, "User reader see creator's line")

        ids = distribution_list_model.search(self.cr, user_creator.id, [('id', '=', id_distribution_list)])
        self.assertEqual(len(ids), 1, "User creator doesn't see its distribution")
        ids = distribution_list_model.search(self.cr, user_no_access.id, [('id', '=', id_distribution_list)])
        self.assertEqual(len(ids), 0, "User reader see creator's distribution")

    def test_compute_distribution_list_ids(self):

        user_model = self.registry('res.users')
        partner_model = self.registry('res.partner')
        distribution_list_model = self.registry('distribution.list')
        distribution_list_line_model = self.registry('distribution.list.line')

        user_ids = user_model.search(self.cr, self.uid, [])
        users = user_model.browse(self.cr, self.uid, user_ids)
        user_creator = users[1]

        id_customer = partner_model.create(self.cr, user_creator.id, {
            'active': True,
            'notify_email': 'comment',
            'type': 'contact',
            'is_company': False,
            'lang': 'en_US',
            'child_ids': [],
            'customer': True,
            'user_ids': [],
            'name': 'customer',
            'category_id': [[6, False, []]],
            'company_id': user_creator.company_id.id,
        })
        _logger.info("%s create the partner %s", user_creator.name, id_customer)

        id_supplier = partner_model.create(self.cr, user_creator.id, {
            'active': True,
            'notify_email': 'comment',
            'type': 'contact',
            'is_company': False,
            'lang': 'en_US',
            'child_ids': [],
            'supplier': True,
            'user_ids': [],
            'name': 'supplier',
            'category_id': [[6, False, []]],
            'company_id': user_creator.company_id.id,
        })
        _logger.info("%s create the partner %s", user_creator.name, id_supplier)

        # create distribution_list_line and distribution_list with the first user
        id_distribution_list_line_supplier = distribution_list_line_model.create(self.cr, user_creator.id, {
            'name': 'employee_1',
            'domain': "[[\'supplier\', \'=\', True]]",
            'src_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'company_id': user_creator.company_id.id,
        })

        id_distribution_list_line_customer = distribution_list_line_model.create(self.cr, user_creator.id, {
            'name': 'employee_2',
            'domain': "[[\'customer\', \'=\', True]]",
            'src_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'company_id': user_creator.company_id.id,
        })

        id_distribution_list_cust_supl = distribution_list_model.create(self.cr, user_creator.id, {
            'name': 'tee meeting',
            'company_id': user_creator.company_id.id,
            'dst_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'to_include_distribution_list_line_ids': [[4, id_distribution_list_line_supplier], [4, id_distribution_list_line_customer]]
        })
        _logger.info("%s create the distribution list %s (2 in include)", user_creator, id_distribution_list_cust_supl)

        id_distribution_list_nocust_nosupl = distribution_list_model.create(self.cr, user_creator.id, {
            'name': 'tee meeting 2',
            'company_id': user_creator.company_id.id,
            'dst_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'to_exclude_distribution_list_line_ids': [[4, id_distribution_list_line_supplier], [4, id_distribution_list_line_customer]]
        })
        _logger.info("%s create the distribution list %s (customer and supplier in exclude)", user_creator, id_distribution_list_nocust_nosupl)

        id_distribution_list_cust_nosupl = distribution_list_model.create(self.cr, user_creator.id, {
            'name': 'tee meeting 3',
            'company_id': user_creator.company_id.id,
            'dst_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'to_include_distribution_list_line_ids': [[6, False, [id_distribution_list_line_customer]]],
            'to_exclude_distribution_list_line_ids': [[6, False, [id_distribution_list_line_supplier]]],
        })
        _logger.info("%s create the distribution list %s (customer in include supplier in exclude)", user_creator, id_distribution_list_cust_nosupl)

        list_ids_cust_supl = distribution_list_model.get_ids_from_distribution_list(self.cr, user_creator.id, [id_distribution_list_cust_supl], context=None)
        self.assertEqual(id_customer in list_ids_cust_supl and id_supplier in list_ids_cust_supl, True, "The ids computed are not corresponded to id_customer and id_supplier")

        list_ids_nocust_nosup = distribution_list_model.get_ids_from_distribution_list(self.cr, user_creator.id, [id_distribution_list_nocust_nosupl], context=None)
        self.assertEqual(id_customer in list_ids_nocust_nosup and id_supplier in list_ids_nocust_nosup, False, "The result must not contain the customer and the supplier id")

        list_ids_cust_nosupl = distribution_list_model.get_ids_from_distribution_list(self.cr, user_creator.id, [id_distribution_list_cust_nosupl], context=None)
        self.assertEqual(id_customer in list_ids_cust_nosupl, True, "The ids computed must be one customer only")

    def test_complete_distribution_list(self):
        """
        ===============================
        test_complete_distribution_list
        ===============================
        1) Create 3 filters and 2 distribution lists
        dl one to_include: 1
        dl two to_include: 1
        dl two to_exclude: 1

        2) complete dl 1 with dl 2.
        3) Check that dl
            * has two filters ``to_include``
            * has one filter ``to_exclude``
        """
        cr = self.cr
        dl_model = self.registry('distribution.list')
        dl_line_model = self.registry('distribution.list.line')
        dl_line_names = ['a', 'b', 'c']
        dl_line_ids = []
        dst_model_id = self.registry('ir.model').search(cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        for dl_line_name in dl_line_names:
            dl_line_ids.append(dl_line_model.create(cr, SUPERUSER_ID, {'name': dl_line_name,
                                                    'src_model_id': dst_model_id}))

        src_dist_id = dl_model.create(cr, SUPERUSER_ID, {'name': 'src',
                                                              'dst_model_id': dst_model_id,
                                                              'to_include_distribution_list_line_ids': [[6, False, [dl_line_ids[1]]]],
                                                              'to_exclude_distribution_list_line_ids': [[6, False, [dl_line_ids[2]]]]})
        trg_dist_id = dl_model.create(cr, SUPERUSER_ID, {'name': 'trg',
                                                              'dst_model_id': dst_model_id,
                                                              'to_include_distribution_list_line_ids': [[6, False, [dl_line_ids[0]]]]})
        dl_model.complete_distribution_list(cr, SUPERUSER_ID, [trg_dist_id], [src_dist_id])
        dl_values = dl_model.read(cr, SUPERUSER_ID, [trg_dist_id], ['to_include_distribution_list_line_ids',
                                                                    'to_exclude_distribution_list_line_ids'])[0]
        self.assertTrue(len(dl_values['to_include_distribution_list_line_ids']) == 2, 'Distribution List Should have 2 filters to include')
        self.assertTrue(len(dl_values['to_exclude_distribution_list_line_ids']) == 1, 'Distribution List Should have 1 filters to exclude')

    def test_get_complex_distribution_list_ids(self):
        """
        =================================
        get_complex_distribution_list_ids
        =================================
        """
        partner_model = self.registry('res.partner')
        distribution_list_model = self.registry('distribution.list')
        distribution_list_line_model = self.registry('distribution.list.line')
        cr = self.cr

        p8 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p8 more_filter filter_three'})
        p7 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p7 filter_three',
                                                     'parent_id': p8})

        p6 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p6'})
        p5 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p5'})
        p4 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p4',
                                                     'parent_id': p5})
        p3 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p3 filter_two',
                                                     'parent_id': p6})

        p2 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p2 filter_one',
                                                     'parent_id': p4})
        p1 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p1 filter_one',
                                                     'parent_id': p4})
        partner_model_id = self.registry('ir.model').search(self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]
        filter_one = distribution_list_line_model.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_one',
            'domain': "[[\'name\', \'ilike\', \'filter_one\']]",
            'src_model_id': partner_model_id,
        })
        filter_two = distribution_list_line_model.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_two',
            'domain': "[[\'name\', \'ilike\', \'filter_two\']]",
            'src_model_id': partner_model_id,
        })
        filter_three = distribution_list_line_model.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_three',
            'domain': "[[\'name\', \'ilike\', \'filter_three\']]",
            'src_model_id': partner_model_id,
        })

        dl = distribution_list_model.create(self.cr, SUPERUSER_ID, {'name': 'get_complex_distribution_list_ids',
                                                              'dst_model_id': partner_model_id,
                                                              'bridge_field': 'parent_id',
                                                              'to_include_distribution_list_line_ids': [[6, False, [filter_one, filter_two, filter_three]]]})
        context = {
           'more_filter': ["('name', 'not ilike', 'more_filter')"],
           'sort_by': 'name desc',
           'field_alternative_object': 'company_id',
           'field_main_object': 'parent_id',
        }
        res_ids, alternative_ids = distribution_list_model.get_complex_distribution_list_ids(cr, SUPERUSER_ID, [dl], context=context)
        self.assertTrue(res_ids == [p5], 'Should have p5 partner has result')
        self.assertTrue(len(alternative_ids) == 1, 'Should have at least one company as alternative object')

    def test_duplicate_distribution_list_and_filters(self):
        """
        Test the duplication (copy) of a distribution list and a filter
        """
        distribution_list_model = self.registry('distribution.list')
        distribution_list_line_model = self.registry('distribution.list.line')

        user_id = self.ref("distribution_list.first_user")

        # create distribution_list_line and distribution_list
        id_distribution_list_line = distribution_list_line_model.create(self.cr, user_id, {
            'name': 'employee to copy',
            'domain': "[[\'employee\', \'=\', True]]",
            'src_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
        })
        _logger.info("create the distribution list line %s", id_distribution_list_line)

        id_distribution_list = distribution_list_model.create(self.cr, user_id, {
            'name': 'tea meeting to copy',
            'dst_model_id': self.registry('ir.model').search(self.cr, self.uid, [('model', '=', 'res.partner')])[0],
            'to_include_distribution_list_line_ids': [[4, id_distribution_list_line]],
        })
        _logger.info("create the distribution list %s", id_distribution_list)

        fields_to_not_compare = ['id', 'name']
        id_distribution_list_copy = distribution_list_model.copy(self.cr, user_id, id_distribution_list)
        _logger.info("copy the distribution list %s", id_distribution_list)
        read_dl = distribution_list_model.read(self.cr, user_id, id_distribution_list)
        for field in fields_to_not_compare:
            del read_dl[field]
        read_dl_copy = distribution_list_model.read(self.cr, user_id, id_distribution_list_copy)
        for field in fields_to_not_compare:
            del read_dl_copy[field]
        self.assertEqual(read_dl, read_dl_copy)

        fields_to_not_compare = ['id', 'name']
        id_distribution_list_line_copy = distribution_list_line_model.copy(self.cr, user_id, id_distribution_list_line)
        _logger.info("copy the distribution list line %s", id_distribution_list_line)
        read_dl = distribution_list_line_model.read(self.cr, user_id, id_distribution_list_line)
        for field in fields_to_not_compare:
            del read_dl[field]
        read_dl_copy = distribution_list_line_model.read(self.cr, user_id, id_distribution_list_line_copy)
        for field in fields_to_not_compare:
            del read_dl_copy[field]
        self.assertEqual(read_dl, read_dl_copy)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
