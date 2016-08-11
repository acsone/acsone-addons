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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class MergeDistributionList(orm.TransientModel):
    _name = 'merge.distribution.list'
    _description = 'Merge Distribution Lists Wizard'

    _columns = {
        'distribution_list_id': fields.many2one(
            'distribution.list',
            'Distribution List to Complete', required=True),
    }

    def merge_distribution_list(self, cr, uid, ids, context=None):
        """
        Call ``complete_distribution_list`` with distribution.list
        passing on hand the selected distribution list id and on the other the
        ids of the ``active_ids``

        :param context: key ``active_ids`` contains the ids of distribution
                        that will complete the selected distribution list
                        of the wizard
        :raise orm.except_orm: If no ids into the value of ``active_ids`` or
                               no key ``active_ids`` into the context.
        """
        if len(context.get('active_ids', False) or []) == 0:
            raise orm.except_orm(
                _('Error'),
                _('At least one distribution list must be selected'))
        trg_dist_list_ids = []
        for wiz in self.browse(cr, uid, ids, context=context):
            trg_dist_list_ids.append(wiz.distribution_list_id.id)
        self.pool['distribution.list'].complete_distribution_list(
            cr, uid, trg_dist_list_ids, context['active_ids'], context=context)
