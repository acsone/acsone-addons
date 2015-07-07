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
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp import models, api, fields
from openerp.modules.registry import RegistryManager
from openerp.tools import SUPERUSER_ID
import openerp.tests.common as common
import mock


class test_one2many_groups(SharedSetupTransactionCase):

    def _init_test_model(self, all_cls):
        # mock commit since it"s called in the _auto_init method
        self.cr.commit = mock.MagicMock()
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
            _description = 'Dummy Model'

            name = fields.Char(string='Name')
            member_model_ids = fields.One2many(
                comodel_name='member.model', inverse_name='dummy_model_id')

        class DummyModelGroup(models.Model):
            _name = 'dummy.model.group'
            _inherit = 'abstract.group'
            _description = 'Dummy Model Group'
            _complementary_fields = ['total']

            @api.one
            @api.depends('members_ids.total')
            def compute_total(self):
                total = 'total'
                super(DummyModelGroup, self).compute_complementary_field(total)

            parent_id = fields.Many2one(comodel_name='dummy.model.group')
            children_ids = fields.One2many(comodel_name='dummy.model.group')
            master_id = fields.Many2one(comodel_name='dummy.model')
            members_ids = fields.One2many(comodel_name='member.model')
            total = fields.Integer(
                compute='compute_total', string='total', store=True)

        self._init_test_model([MemberModel, DummyModel, DummyModelGroup])
        super(test_one2many_groups, self).setUp()
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
