# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of one2many_groups,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     one2many_groups is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     one2many_groups is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with one2many_groups.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
from openerp import models, api, fields
from openerp.modules.registry import RegistryManager
from openerp.tools import SUPERUSER_ID
import openerp.tests.common as common
from .data import VIEW_REPORT_ARCH, VIEW_REPORT_DOCUMENT_ARCH


class test_one2many_groups(common.TransactionCase):

    _module_ns = 'one2many_groups'

    def _init_test_model(self, all_cls):
        pool = RegistryManager.get(common.DB)
        all_inst = []
        for cls in all_cls:
            inst = cls._build_model(pool, self.cr)
            inst._prepare_setup(self.cr, SUPERUSER_ID)
            inst._setup_base(self.cr, SUPERUSER_ID, partial=False)
            all_inst.append(inst)
        for inst in all_inst:
            inst._setup_fields(self.cr, SUPERUSER_ID)
            inst._setup_complete(self.cr, SUPERUSER_ID)
        for inst in all_inst:
            inst._auto_init(self.cr, {'module': __name__})

    def setUp(self):
        common.TransactionCase.setUp(self)

        class MemberModel(models.Model):
            _name = 'member.model'
            _inherit = ['abstract.group.member']
            _cls_group = 'dummy.model.group'
            _master_relation = 'dummy_model_id'

            name = fields.Char(string='Name')
            total = fields.Integer(string='Total')
            dummy_model_id = fields.Char(string='Dummy Model')
            abstract_group_id = fields.Many2one(
                comodel_name='dummy.model.group')

        class DummyModel(models.Model):
            _name = 'dummy.model'
            _inherit = 'abstract.group.master'
            _description = 'Dummy Model'
            _member_relation = 'member_model_ids'

            name = fields.Char(string='Name')
            member_model_ids = fields.One2many(
                comodel_name='member.model', inverse_name='dummy_model_id',
                copy=True)
            abstract_group_ids = fields.One2many(
                comodel_name='dummy.model.group', inverse_name='master_id',
                string='Groups', copy=True)

        class DummyModelGroup(models.Model):
            _name = 'dummy.model.group'
            _inherit = 'abstract.group'
            _description = 'Dummy Model Group'
            _complementary_fields = ['total']

            @api.one
            @api.depends(
                'members_ids.total', 'members_ids', 'children_ids',
                'children_ids.total')
            def compute_total(self):
                total = 'total'
                super(DummyModelGroup, self).compute_complementary_field(total)

            parent_id = fields.Many2one(comodel_name='dummy.model.group')
            children_ids = fields.One2many(comodel_name='dummy.model.group')
            master_id = fields.Many2one(comodel_name='dummy.model')
            members_ids = fields.One2many(comodel_name='member.model')
            total = fields.Float(
                compute='compute_total', string='total', store=True)

        self._init_test_model([MemberModel, DummyModel, DummyModelGroup])
        self.dummy_model_group_obj = self.env['dummy.model.group']
        self.dummy_model_obj = self.env['dummy.model']
        self.member_model_obj = self.env['member.model']

    def test_model(self):
        vals = {
            'name': 'Test'
        }
        master_id = self.dummy_model_obj.create(vals)
        member_vals = {
            'name': 'Test',
            'total': 10,
            'dummy_model_id': master_id.id
        }
        member_id = self.member_model_obj.create(member_vals)
        r_sum = member_id.total
        vals = {
            'name': 'Root',
            'master_id': master_id.id,
            'parent_id': False,
            'members_ids': [6, False, [member_id.id]],
        }
        root_id = self.dummy_model_group_obj.create(vals)
        self.assertEqual(root_id.sequence, 1, 'Should have a sequence of 1')
        self.assertEqual(root_id.level, 1, 'Should have a level of 1')
        self.assertEqual(
            root_id.total, r_sum, 'Should have a total of %s' % r_sum)
        vals = {
            'name': '11',
            'master_id': master_id.id,
            'parent_id': root_id.id,
        }
        child_11 = self.dummy_model_group_obj.create(vals)
        member_id_11 = self.member_model_obj.create(member_vals)
        r_sum += member_id.total
        child_11.members_ids = [member_id_11.id]
        vals = {
            'name': '12',
            'master_id': master_id.id,
            'parent_id': root_id.id,
        }
        child_12 = self.dummy_model_group_obj.create(vals)
        self.assertEqual(child_11.sequence, 1, 'Should have a sequence of 1')
        self.assertEqual(child_11.level, 2, 'Should have a level of 2')
        self.assertEqual(child_12.sequence, 2, 'Should have a sequence of 2')
        self.assertEqual(child_12.level, 2, 'Should have a level of 2')
        self.assertEqual(
            root_id.total, r_sum, 'Should have a total of %s' % r_sum)
        self.assertTrue(
            child_12.get_move_group_ids(), 'Should have ids')
        self.assertTrue(
            root_id.get_move_group_ids(), 'Should not have ids')
        child_12.sequence = 1
        self.assertEqual(child_12.sequence, 1, 'Should have a sequence of 1')
        self.assertEqual(child_11.sequence, 2, 'Should have a sequence of 2')
        child_12.parent_id = False
        self.assertEqual(child_12.sequence, 2, 'Should have a sequence of 2')
        self.assertEqual(child_12.level, 1, 'Should have a sequence of 1')
        member_vals = {
            'name': 'Test',
            'total': 10,
            'dummy_model_id': master_id.id
        }
        m3 = self.member_model_obj.create(member_vals)
        child_12.members_ids = [m3.id]
        child_12.with_context(recomute=True).write({
            'parent_id': child_11.id
        })
        self.assertEqual(child_11.total, child_12.total * 2,
                         'Total 11 should be the *2 than total 12')
        self.assertEqual(
            root_id.total, child_11.total + root_id.members_ids[0].total,
            'Total root should be total 11(no others children)')

        master_id_copied = master_id.copy()
        self.assertEqual(len(master_id_copied.abstract_group_ids), 3)
        self.assertEqual(len(master_id_copied.member_model_ids), 3)
        for i in range(0, 3):
            self.assertNotEqual(master_id_copied.abstract_group_ids[i].id,
                                master_id.abstract_group_ids[i].id)
            self.assertEqual(
                master_id_copied.abstract_group_ids[i].copy_origin_id.id,
                master_id.abstract_group_ids[i].id)
            self.assertNotEqual(
                master_id_copied.member_model_ids[i].abstract_group_id.id,
                master_id.member_model_ids[i].abstract_group_id.id)

    def test_report(self):
        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context
        report_document_name = '%s.report_dummy_document' % self._module_ns
        report_name = '%s.report_dummy' % self._module_ns
        vals = {
            'name': 'report_dummy_document',
            'type': 'qweb',
            'mode': 'primary',
            'xml_id': report_document_name,
            'arch': VIEW_REPORT_DOCUMENT_ARCH
        }
        view_id = self.env['ir.ui.view'].create(vals)
        vals = {
            'module': self._module_ns,
            'name': 'report_dummy_document',
            'model': 'ir.ui.view',
            'res_id': view_id.id,
        }
        self.env['ir.model.data'].create(vals)
        vals = {
            'name': 'report_dummy',
            'type': 'qweb',
            'mode': 'primary',
            'xml_id': report_name,
            'arch': VIEW_REPORT_ARCH
        }
        view_id = self.env['ir.ui.view'].create(vals)
        vals = {
            'module': self._module_ns,
            'name': 'report_dummy',
            'model': 'ir.ui.view',
            'res_id': view_id.id,
        }
        self.env['ir.model.data'].create(vals)
        vals = {
            'name': 'Dummy Report',
            'tree_grid_model': 'dummy.model.group',
            'model': 'dummy.model',
            'report_file': report_name,
            'report_name': report_name,
            'report_type': 'qweb-pdf',
        }
        self.env['ir.actions.report.xml'].create(vals)
        vals = {
            'name': 'Test'
        }
        master_id = self.dummy_model_obj.create(vals)
        member_vals = {
            'total': 10,
            'dummy_model_id': master_id.id
        }
        member_ids = []
        for i in xrange(3):
            member_vals['name'] = 'test-%s' % i
            member_ids.append(self.member_model_obj.create(member_vals))

        vals = {
            'master_id': master_id.id,
        }
        group_ids = []
        for i in xrange(3):
            vals['members_ids'] = [[6, False, [member_ids[i].id]]]
            vals['name'] = 'level %s seq 1' % (i + 1)
            values = vals.copy()
            group_id = self.dummy_model_group_obj.create(values)
            group_ids.append(group_id)
            vals['parent_id'] = group_id.id
        ctx = context.copy()
        ctx['translatable'] = True
        res = self.registry['report'].get_html(
            cr, uid, [master_id.id], report_name, data=None, context=ctx)
        html = etree.HTML(res)
        table = html.find('.//table[@tree_grid_mode]')
        self.assertTrue(
            table, 'Should have a table with tag`html_tree_grid_mode`')
        all_tr = table.findall('.//tbody//tr')
        self.assertEquals(
            len(group_ids) + len(member_ids), len(all_tr),
            'Should have one <tr> for each group/member')
        all_true = []
        all_true.append(
            all_tr[0].attrib['data-oe-group_id'] == str(group_ids[0].id))
        all_true.append(
            all_tr[1].attrib['data-oe-group_id'] == str(group_ids[0].id))
        all_true.append(
            all_tr[1].find('.//td//span').attrib['data-oe-id'] ==
            str(group_ids[0].members_ids[0].id))
        all_true.append(
            all_tr[2].attrib['data-oe-group_id'] == str(group_ids[1].id))
        all_true.append(
            all_tr[3].attrib['data-oe-group_id'] == str(group_ids[1].id))
        all_true.append(
            all_tr[3].find('.//td//span').attrib['data-oe-id'] ==
            str(group_ids[1].members_ids[0].id))
        all_true.append(
            all_tr[4].attrib['data-oe-group_id'] == str(group_ids[2].id))
        all_true.append(
            all_tr[5].attrib['data-oe-group_id'] == str(group_ids[2].id))
        all_true.append(
            all_tr[5].find('.//td//span').attrib['data-oe-id'] ==
            str(group_ids[2].members_ids[0].id))
        self.assertTrue(all(all_true), 'Should be true match for all')
