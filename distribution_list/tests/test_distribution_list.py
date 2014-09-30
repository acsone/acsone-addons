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
import os

from openerp.osv import orm
from openerp import tools
from openerp.tools import convert_xml_import
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
SUPERUSER_ID = common.ADMIN_USER_ID


def get_file(module_name, fp):
    pathname = os.path.join(module_name, fp)
    return tools.file_open(pathname)


def load_data(cr, module_name, fp, idref=None, mode='init', noupdate=False,
              report=None):
    pathname = os.path.join(module_name, fp)
    fp = get_file(module_name, fp)
    _logger.info("Import datas from %s" % pathname)
    try:
        convert_xml_import(cr, module_name, fp, idref, mode, noupdate, report)
    except:
        _logger.info("%s already exists in database" % fp)
        pass


class test_distribution_list(common.TransactionCase):

    def setUp(self):
        super(test_distribution_list, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        load_data(self.cr, 'distribution_list', "tests/data/company_data.xml")
        load_data(self.cr, 'distribution_list', "tests/data/user_data.xml")

    def test_confidentiality_distribution_list(self):

        user_model = self.registry('res.users')
        distri_list_obj = self.registry('distribution.list')
        distri_list__line_obj = self.registry('distribution.list.line')

        user_id_1 = user_model.search(
            self.cr, self.uid, [('login', '=', 'first')])[0]
        user_id_2 = user_model.search(
            self.cr, self.uid, [('login', '=', 'second')])[0]
        user_creator = user_model.browse(
            self.cr, self.uid, user_id_1, context={})
        user_no_access = user_model.browse(
            self.cr, self.uid, user_id_2, context={})

        # create distribution_list_line and distribution_list with the first
        # user
        id_distribution_list_line = distri_list__line_obj.create(
            self.cr, user_creator.id,
            {'name': 'employee',
             'domain': "[[\'employee\', \'=\', True]]",
             'src_model_id': self.registry('ir.model').search(
                 self.cr, self.uid, [('model', '=', 'res.partner')])[0],
             'company_id': user_creator.company_id.id,
             })
        _logger.info("%s create the distribution list line %s",
                     user_creator.name, id_distribution_list_line)

        id_distribution_list = distri_list_obj.create(
            self.cr, user_creator.id,
            {'name': 'tee meeting',
             'company_id': user_creator.company_id.id,
             'dst_model_id': self.registry('ir.model').search(
                 self.cr, self.uid, [('model', '=', 'res.partner')])[0],
             'to_include_distribution_list_line_ids':
                [[4, id_distribution_list_line]],
             })
        _logger.info("%s create the distribution list %s",
                     user_creator, id_distribution_list)

        ids = distri_list__line_obj.search(
            self.cr, user_creator.id,
            [('id', '=', id_distribution_list_line)])
        self.assertEqual(len(ids), 1, "User creator doesn't see its line")
        ids = distri_list__line_obj.search(
            self.cr, user_no_access.id,
            [('id', '=', id_distribution_list_line)])
        self.assertEqual(len(ids), 0, "User reader see creator's line")

        ids = distri_list_obj.search(
            self.cr, user_creator.id, [('id', '=', id_distribution_list)])
        self.assertEqual(
            len(ids), 1, "User creator doesn't see its distribution")
        ids = distri_list_obj.search(
            self.cr, user_no_access.id, [('id', '=', id_distribution_list)])
        self.assertEqual(len(ids), 0, "User reader see creator's distribution")

    def test_compute_distribution_list_ids(self):

        user_model = self.registry('res.users')
        partner_model = self.registry('res.partner')
        distri_list_obj = self.registry('distribution.list')
        distri_list__line_obj = self.registry('distribution.list.line')

        user_ids = user_model.search(self.cr, self.uid, [])
        users = user_model.browse(self.cr, self.uid, user_ids)
        user_creator = users[1]

        id_customer = partner_model.create(self.cr, user_creator.id, {
            'active': True,
            'notify_email': 'none',
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
        _logger.info("%s create the partner %s", user_creator.name,
                     id_customer)

        id_supplier = partner_model.create(self.cr, user_creator.id, {
            'active': True,
            'notify_email': 'none',
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
        _logger.info("%s create the partner %s", user_creator.name,
                     id_supplier)

        # create distribution_list_line and distribution_list with the first
        # user
        dst_model_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]
        id_distribution_list_line_supplier = distri_list__line_obj.create(
            self.cr, user_creator.id,
            {'name': 'employee_1',
             'domain': "[[\'supplier\', \'=\', True]]",
             'src_model_id': dst_model_id,
             'company_id': user_creator.company_id.id,
             })

        id_distribution_list_line_customer = distri_list__line_obj.create(
            self.cr, user_creator.id,
            {'name': 'employee_2',
             'domain': "[[\'customer\', \'=\', True]]",
             'src_model_id': dst_model_id,
             'company_id': user_creator.company_id.id,
             })

        id_distribution_list_cust_supl = distri_list_obj.create(
            self.cr, user_creator.id,
            {'name': 'tee meeting',
             'company_id': user_creator.company_id.id,
             'dst_model_id': dst_model_id,
             'to_include_distribution_list_line_ids': [
                 [4, id_distribution_list_line_supplier],
                 [4, id_distribution_list_line_customer]]
             })
        _logger.info("%s create the distribution list %s (2 in include)",
                     user_creator, id_distribution_list_cust_supl)

        id_distribution_list_nocust_nosupl = distri_list_obj.create(
            self.cr, user_creator.id,
            {'name': 'tee meeting 2',
             'company_id': user_creator.company_id.id,
             'dst_model_id': dst_model_id,
             'to_exclude_distribution_list_line_ids':
                 [[4, id_distribution_list_line_supplier],
                  [4, id_distribution_list_line_customer]]
             })
        _logger.info(
            '%s create the distribution list %s '
            '(customer and supplier in exclude)',
            user_creator, id_distribution_list_nocust_nosupl)

        id_distribution_list_cust_nosupl = distri_list_obj.create(
            self.cr, user_creator.id,
            {'name': 'tee meeting 3',
             'company_id': user_creator.company_id.id,
             'dst_model_id': dst_model_id,
             'to_include_distribution_list_line_ids':
                 [[6, False, [id_distribution_list_line_customer]]],
             'to_exclude_distribution_list_line_ids':
                 [[6, False, [id_distribution_list_line_supplier]]],
             })
        _logger.info(
            '%s create the distribution list %s (customer in include supplier '
            'in exclude)', user_creator, id_distribution_list_cust_nosupl)

        list_ids_cust_supl = distri_list_obj.get_ids_from_distribution_list(
            self.cr, user_creator.id, [id_distribution_list_cust_supl],
            context=None)

        self.assertEqual(
            id_customer in list_ids_cust_supl and
            id_supplier in list_ids_cust_supl,
            True,
            'The ids computed are not corresponded to id_customer and '
            'id_supplier')

        list_ids_nocust_nosup = distri_list_obj.get_ids_from_distribution_list(
            self.cr, user_creator.id, [id_distribution_list_nocust_nosupl],
            context=None)
        self.assertEqual(
            id_customer in list_ids_nocust_nosup and
            id_supplier in list_ids_nocust_nosup,
            False,
            "The result must not contain the customer and the supplier id")

        list_ids_cust_nosupl = distri_list_obj.get_ids_from_distribution_list(
            self.cr, user_creator.id, [id_distribution_list_cust_nosupl],
            context=None)
        self.assertEqual(id_customer in list_ids_cust_nosupl,
                         True, "The ids computed must be one customer only")

    def test_not_safe_mode(self):
        """
        Test that excluded ids from excluded filters of distribution list are
        not removed from the resulting ids if they are included by filters
        into another distribution list
        ex:
        -------- DL1 ------------------ DL2 --------
        include   |  exclude || include  |  exclude
            A     |    B     ||    B     |    A
            -----------------------------------
            result: [A,B] with safe_mode = False
        """
        cr, uid, context = self.cr, self.uid, {'safe_mode': False}
        partner_model = self.registry('res.partner')
        distri_list_obj = self.registry('distribution.list')
        distri_list_line_obj = self.registry('distribution.list.line')

        partner_name_1 = '%s' % uuid4()
        partner_name_2 = '%s' % uuid4()

        partner_id1 = partner_model.create(cr, uid, {
            'name': '%s' % partner_name_1,
        })
        partner_id2 = partner_model.create(cr, uid, {
            'name': '%s' % partner_name_2,
        })
        dst_model_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]

        distri_line_partner1 = distri_list_line_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'domain': "[['name', '=', '%s']]" % partner_name_1,
                'src_model_id': dst_model_id
            })

        distri_line_partner2 = distri_list_line_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'domain': "[['name', '=', '%s']]" % partner_name_2,
                'src_model_id': dst_model_id,
            })

        include1_exclude2 = distri_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': dst_model_id,
                'to_include_distribution_list_line_ids':
                    [[4, distri_line_partner1]],
                'to_exclude_distribution_list_line_ids':
                    [[4, distri_line_partner2]],
            })
        include2_exclude1 = distri_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': dst_model_id,
                'to_include_distribution_list_line_ids':
                    [[4, distri_line_partner2]],
                'to_exclude_distribution_list_line_ids':
                    [[4, distri_line_partner1]],
            })

        waiting_list_ids = distri_list_obj.get_ids_from_distribution_list(
            cr, uid, [include2_exclude1, include1_exclude2], safe_mode=False,
            context=context)
        self.assertTrue(len(waiting_list_ids) == 2, "Should Have two id")
        self.assertTrue(partner_id1 in waiting_list_ids, "'partner_id1'\
            should not be excluded from the result into safe_mode False")
        self.assertTrue(partner_id2 in waiting_list_ids, "'partner_id2'\
            should not be excluded from the result into safe_mode False")

    def test_get_ids_from_distribution_list(self):
        """
        Will check that
        * calling `get_ids_from_distribution_list` with two distribution list
            that have two different model will raise `orm` exception
        * calling them with same model is OK
        """
        cr, uid, context = self.cr, self.uid, {}
        distribution_list_obj = self.registry['distribution.list']

        partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]
        template_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'email.template')])[0]

        distribution_list_id1 = distribution_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': partner_model_id,
            })
        distribution_list_id2 = distribution_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': partner_model_id,
            })
        distribution_list_id3 = distribution_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': template_model_id,
            })
        will_failed_ids = [distribution_list_id1, distribution_list_id3]
        will_succeed_ids = [distribution_list_id1, distribution_list_id2]

        distribution_list_obj.get_ids_from_distribution_list(
            cr, uid, will_succeed_ids, context=context)

        self.assertRaises(orm.except_orm,
                          distribution_list_obj.get_ids_from_distribution_list,
                          cr, uid, will_failed_ids, context=context)

    def test_complete_distribution_list(self):
        """
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
        dst_model_id = self.registry('ir.model').search(
            cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        for dl_line_name in dl_line_names:
            dl_line_ids.append(
                dl_line_model.create(
                    cr, SUPERUSER_ID, {'name': dl_line_name,
                                       'src_model_id': dst_model_id}))

        src_dist_id = dl_model.create(
            cr, SUPERUSER_ID,
            {'name': 'src',
             'dst_model_id': dst_model_id,
             'to_include_distribution_list_line_ids':
                 [[6, False, [dl_line_ids[1]]]],
             'to_exclude_distribution_list_line_ids':
                 [[6, False, [dl_line_ids[2]]]]})
        trg_dist_id = dl_model.create(
            cr, SUPERUSER_ID, {'name': 'trg',
                               'dst_model_id': dst_model_id,
                               'to_include_distribution_list_line_ids':
                                   [[6, False, [dl_line_ids[0]]]]})
        dl_model.complete_distribution_list(
            cr, SUPERUSER_ID, [trg_dist_id], [src_dist_id])
        dl_values = dl_model.read(
            cr, SUPERUSER_ID, [
                trg_dist_id], ['to_include_distribution_list_line_ids',
                               'to_exclude_distribution_list_line_ids'])[0]
        self.assertTrue(len(dl_values['to_include_distribution_list_line_ids'])
                        == 2,
                        'Distribution List Should have 2 filters to include')
        self.assertTrue(len(dl_values['to_exclude_distribution_list_line_ids'])
                        == 1,
                        'Distribution List Should have 1 filters to exclude')

    def test_get_complex_distribution_list_ids(self):
        """
        Test that `get_complex_distribution_list_ids` return the correct ids
        when use a context with
        * more_filter
        * sort_by
        * field_alternative_object
        * field_main_object
        """
        partner_model = self.registry('res.partner')
        distri_list_obj = self.registry('distribution.list')
        distri_list__line_obj = self.registry('distribution.list.line')
        cr = self.cr

        p9 = partner_model.create(
            cr, SUPERUSER_ID, {'name': 'p9'})
        p8 = partner_model.create(
            cr, SUPERUSER_ID, {'name': 'p8 more_filter filter_three',
                               'parent_id': p9})
        partner_model.create(
            cr, SUPERUSER_ID, {'name': 'p7 more_filter filter_three',
                               'parent_id': p8})

        p6 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p6'})
        p5 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p5'})
        p4 = partner_model.create(cr, SUPERUSER_ID, {'name': 'p4',
                                                     'parent_id': p5})
        partner_model.create(cr, SUPERUSER_ID, {'name': 'p3 filter_two',
                                                'parent_id': p6})

        partner_model.create(cr, SUPERUSER_ID, {'name': 'p2 filter_one',
                                                'parent_id': p4})
        partner_model.create(cr, SUPERUSER_ID, {'name': 'p1 filter_one',
                                                'parent_id': p4})
        partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]
        filter_one = distri_list__line_obj.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_one',
            'domain': "[[\'name\', \'ilike\', \'filter_one\']]",
            'src_model_id': partner_model_id,
        })
        filter_two = distri_list__line_obj.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_two',
            'domain': "[[\'name\', \'ilike\', \'filter_two\']]",
            'src_model_id': partner_model_id,
        })
        filter_three = distri_list__line_obj.create(self.cr, SUPERUSER_ID, {
            'name': 'filter_three',
            'domain': "[[\'name\', \'ilike\', \'filter_three\']]",
            'src_model_id': partner_model_id,
        })

        dl = distri_list_obj.create(
            self.cr, SUPERUSER_ID,
            {'name': 'get_complex_distribution_list_ids',
             'dst_model_id': partner_model_id,
             'bridge_field': 'parent_id',
             'to_include_distribution_list_line_ids':
                 [[6, False, [filter_one, filter_two, filter_three]]]})
        context = {
            'more_filter': ["('name', '=', 'p4')"],
            'sort_by': 'name desc',
            'field_alternative_object': 'company_id',
            'field_main_object': 'parent_id',
        }
        res_ids, alt_ids = distri_list_obj.get_complex_distribution_list_ids(
            cr, SUPERUSER_ID, [dl], context=context)
        self.assertTrue(res_ids == [p5], 'Should have p5 partner has result')
        self.assertTrue(
            len(alt_ids) == 1,
            'Should have at least one company as alternative object')

        context.pop('more_filter')
        res_ids, alt_ids = distri_list_obj.get_complex_distribution_list_ids(
            cr, SUPERUSER_ID, [dl], context=context)

        self.assertTrue(len(res_ids) == 2,
                        'Should have 2 ids if no `more_filter`')

    def test_duplicate_distribution_list_and_filters(self):
        """
        Test the duplication (copy) of a distribution list and a filter
        """
        distri_list_obj = self.registry('distribution.list')
        distri_list_line_obj = self.registry('distribution.list.line')

        user_id = self.ref("distribution_list.first_user")

        # create distribution_list_line and distribution_list
        dst_model_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]
        id_distribution_list_line = distri_list_line_obj.create(
            self.cr, user_id,
            {'name': 'employee to copy',
             'domain': "[[\'employee\', \'=\', True]]",
             'src_model_id': dst_model_id,
             })
        _logger.info(
            "create the distribution list line %s", id_distribution_list_line)

        id_distribution_list = distri_list_obj.create(
            self.cr, user_id,
            {'name': 'tea meeting to copy',
             'dst_model_id': dst_model_id,
             'to_include_distribution_list_line_ids':
                 [[4, id_distribution_list_line]],
             })
        _logger.info("create the distribution list %s", id_distribution_list)

        fields_to_not_compare = ['id', 'name', 'display_name']
        id_distribution_list_copy = distri_list_obj.copy(
            self.cr, user_id, id_distribution_list)
        _logger.info("copy the distribution list %s", id_distribution_list)
        read_dl = distri_list_obj.read(
            self.cr, user_id, id_distribution_list)
        for field in fields_to_not_compare:
            del read_dl[field]
        read_dl_copy = distri_list_obj.read(
            self.cr, user_id, id_distribution_list_copy)
        for field in fields_to_not_compare:
            del read_dl_copy[field]
        self.assertEqual(read_dl, read_dl_copy)

        id_distribution_list_line_copy = distri_list_line_obj.copy(
            self.cr, user_id, id_distribution_list_line)
        _logger.info(
            "copy the distribution list line %s", id_distribution_list_line)
        read_dl = distri_list_line_obj.read(
            self.cr, user_id, id_distribution_list_line)
        for field in fields_to_not_compare:
            del read_dl[field]
        read_dl_copy = distri_list_line_obj.read(
            self.cr, user_id, id_distribution_list_line_copy)
        for field in fields_to_not_compare:
            del read_dl_copy[field]
        self.assertEqual(read_dl, read_dl_copy)

    def test_order_del(self):
        """
        check that removing element does not degrade order of the list
        """
        cr, uid, context = self.cr, self.uid, {}
        distribution_list_obj = self.registry['distribution.list']
        with_duplicate_list = [8, 5, 7, 4, 8, 2, 6, 3, 4]
        without_duplicate = [8, 5, 7, 4, 2, 6, 3]
        self.assertEqual(distribution_list_obj._order_del(
            cr, uid, with_duplicate_list, context=context),
            without_duplicate, "Should be the same list into the same order")

    def test_mass_mailing(self):
        """
        Test that action is well returned with correct value required for
        a mass mailing
        """
        cr, uid, context = self.cr, self.uid, {}
        distribution_list_obj = self.registry['distribution.list']
        partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        distribution_list_id = distribution_list_obj.create(
            cr, uid, {
                'name': '%s' % uuid4(),
                'dst_model_id': partner_model_id,
            })
        vals = distribution_list_obj.mass_mailing(
            cr, uid, distribution_list_id, context=context)
        self.assertEqual(vals['type'], 'ir.actions.act_window',
                         "Should be an ir.actions.act_window ")
        self.assertEqual(vals['target'], 'new',
                         "Should be an popup window to avoid lost of focus")
        self.assertEqual(vals['res_model'], 'mail.compose.message',
                         "This mass mailing is made with mail composer")
        # test context content
        self.assertEqual(vals['context']['default_composition_mode'],
                         'mass_mail',
                         "Mass mailing must be launch into mass_mail mode")
        self.assertEqual(vals['context']['active_model'],
                         'res.partner',
                         "Active model must be the same that the\
                         distribution list")
        self.assertEqual(vals['context']['default_distribution_list_id'],
                         distribution_list_id,
                         "default_distribution_list_id must be the same\
                         that the distribution list's id")

    def test_get_action_from_domain(self):
        """
        Test that action is well returned with correct value required for
        a `get_actions_from_domains`
        """
        cr, uid, context = self.cr, self.uid, {}
        distribution_list_obj = self.registry['distribution.list']
        partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        dl_name = '%s' % uuid4()

        distribution_list_id = distribution_list_obj.create(
            cr, uid, {
                'name': '%s' % dl_name,
                'dst_model_id': partner_model_id,
            })
        vals = distribution_list_obj.get_action_from_domains(
            cr, uid, distribution_list_id, context=context)
        self.assertEqual(vals['type'], 'ir.actions.act_window',
                         "Should be an ir.actions.act_window ")
        self.assertEqual(vals['res_model'], 'res.partner',
                         "Model should be the same than the distribution list")
        self.assertEqual(vals['target'], 'new',
                         "Should be an popup window to avoid lost of focus")
