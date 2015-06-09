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

    @api.model
    def get_cls_group(self):
        return self._cls_group

    group_sequence = fields.Integer(string='Group Sequence')
    abstract_group_id = fields.Many2one(
        comodel_name='abstract.group', string='Group')


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

    name = fields.Char(string='Name')
    sequence = fields.Integer(string='Sequence')
    level = fields.Integer(string='Level', required=True)
    parent_id = fields.Many2one(
        comodel_name='abstract.group', string='Parent')
    children_ids = fields.One2many(
        comodel_name='abstract.group', inverse_name='parent_id',
        string='Children')
    master_id = fields.Many2one(
        comodel_name='abstract.group', string='Master Model')
    members_ids = fields.One2many(
        comodel_name='abstract.group.member',
        inverse_name='abstract_group_id', string='Members')
