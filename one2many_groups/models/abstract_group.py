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

from openerp import models, fields, api


class AbstractGroupMember(models.AbstractModel):
    _name = 'abstract.group.member'
    _description = 'Abstract Group Member'
    _cls_group = 'abstract.group'
    _master_relation = None

    @api.model
    def get_cls_group(self):
        return self._cls_group

    abstract_group_id = fields.Many2one(
        comodel_name='abstract.group', ondelete='cascade', string='Group')


class AbstractGroup(models.AbstractModel):
    """
    Fields to be overloaded
    * parent_id: the parent group
    * children_ids: all children groups
    * master_id: Parent Model concerned by the collection
    * members_ids: Line of the Parent Model. Members will be grouped
    """
    _name = 'abstract.group'
    _description = 'Abstract Group'
    _order = 'level,sequence'
    _parent_order = 'sequence'
    _parent_store = True
    _parent_name = 'parent_id'
    _complementary_fields = []

    @api.model
    def get_complementary_fields(self):
        return self._complementary_fields

    @api.multi
    def _compute_sum(self, sum_field):
        self.ensure_one()
        r_sum = 0
        for member in self.members_ids:
            r_sum += getattr(member, sum_field)
        for group in self.children_ids:
            r_sum += getattr(group, sum_field)
        return r_sum

    @api.one
    def compute_complementary_field(self, imp_field):
        """
        Compute `imp_field`

        **Note**
        As children.price_subtotal does not trigger the `parent_id` computation
        then it must be add with `add_toto method`
        """
        setattr(self, imp_field, self._compute_sum(imp_field))
        if self.parent_id:
            self.env.add_todo(
               self._fields.get(imp_field), self.parent_id)

    @api.model
    def _get_last_sequence(self, master_id, parent_id):
        limit = 1
        order = 'sequence desc'
        fields = 'sequence'
        domain = [
            ('master_id', '=', master_id),
            ('parent_id', '=', parent_id)
        ]
        sequence = self.search_read(
            domain, fields=[fields], limit=limit, order=order)
        return sequence and sequence[0][fields] + 1 or 1

    @api.one
    @api.depends('parent_id')
    def compute_level(self):
        if self.parent_id:
            self.level = self.parent_id.level + 1
        else:
            self.level = 1

    @api.one
    @api.depends('name', 'parent_id')
    def compute_display_name(self):
        if self.parent_id:
            self.display_name = '%s/%s' % (self.parent_id.name, self.name)
        else:
            self.display_name = self.name

    @api.one
    def get_move_group_ids(self):
        """
        This method return the group'ids that are not child of the current
        group
        """
        fields = ['display_name', 'sequence']
        domain = [
            ('master_id', '=', self.master_id.id),
            ('id', '!=', self.parent_id.id),
            '|',
            ('parent_left', '<', self.parent_left),
            ('parent_right', '>', self.parent_right),
        ]
        group_parent_ids = self.search_read(domain, fields)
        domain = [
            ('parent_id', '=', self.parent_id.id),
            ('master_id', '=', self.master_id.id),
            ('id', '!=', self.id),
        ]
        group_sequence_ids = self.search_read(domain, fields)
        return [group_sequence_ids, group_parent_ids]

    name = fields.Char(string='Name')
    display_name = fields.Char(
        string='Display Name', compute='compute_display_name')
    sequence = fields.Integer(string='Sequence', default=10)
    level = fields.Integer(string='Level', compute='compute_level', store=True)
    parent_id = fields.Many2one(
        comodel_name='abstract.group', ondelete='cascade', string='Parent')
    parent_left = fields.Integer(select=1)
    parent_right = fields.Integer(select=1)
    children_ids = fields.One2many(
        comodel_name='abstract.group', inverse_name='parent_id',
        string='Children')
    master_id = fields.Many2one(
        comodel_name='abstract.group', string='Master Model')
    members_ids = fields.One2many(
        comodel_name='abstract.group.member',
        inverse_name='abstract_group_id', string='Members')

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        master_id = vals.get('master_id')
        parent_id = vals.get('parent_id')
        vals['sequence'] = self._get_last_sequence(master_id, parent_id)
        if not parent_id:
            domain = [
                (self.members_ids._master_relation, '=', master_id),
                ('abstract_group_id', '=', False),
            ]
            members_ids = self.env[self.members_ids._name].search(domain)
            vals['members_ids'] = [
                (4, member_id) for member_id in members_ids.ids
            ]
        return super(AbstractGroup, self).create(vals)

    @api.one
    def write(self, values):
        parent_id = values.get('parent_id', self.parent_id.id)
        master_id = values.get('master_id', self.master_id.id)
        sequence = values.get('sequence')
        if sequence:
            domain = [
                ('sequence', '>=', sequence),
                ('master_id', '=', master_id),
                ('parent_id', '=', parent_id),
            ]
            vals = {
                'sequence': sequence
            }
            for group in self.search(domain):
                vals['sequence'] += 1
                super(AbstractGroup, group).write(vals)
        elif 'parent_id' in values:
            values['sequence'] =\
                self._get_last_sequence(self.master_id.id, parent_id)
        return super(AbstractGroup, self).write(values)
