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


class DistributionListAddFilter(orm.TransientModel):
    _name = 'distribution.list.add.filter'
    _description = 'Add Filter Wizard'

    def _get_default(self, cr, uid, context=None):
        """
        res: id of the default distribution list if present into the context
        """
        if context is None:
            context = {}
        if 'distribution_list_id' in context:
            return self.pool.get('distribution.list').search(
                cr, uid, [('id', '=', context.get('distribution_list_id'))])[0]
        else:
            return False

    _columns = {
        'distribution_list_id': fields.many2one(
            'distribution.list', 'Distribution List'),
        'distribution_list_line_name': fields.char(
            'Filter Name', size=60, required=True),
        'exclude': fields.boolean(
            'Exclude', help="Check this box to exclude filter result "
                            "from the Distribution List"),
    }

    _defaults = {
        'distribution_list_id':
            lambda self, cr, uid, context:
                self._get_default(cr, uid, context),
        'exclude': False
    }

    def add_distribution_list_line(self, cr, uid, ids, context=None):
        """
         1) Create a distribution list line with the data into the wizard and
            active domain context
         2) Add this distribution list line to the selected
                distribution list in
                    - distribution_list_line_include_id if exclude is False
                    - distribution_list_line_exclude_id if exclude is True
         An exception is raised if no active domain in the context
        """
        if context is None:
            context = {}
        if 'active_domain' not in context:
            raise orm.except_orm(
                _('Error'),
                _('You have to check the entire list to add the current '
                  'filter'))
        domain = context.get('active_domain')

        wizard = self.browse(cr, uid, ids, context)
        name = wizard[0].distribution_list_line_name

        model_name = context.get('active_model')
        model_id = self.pool.get('ir.model').search(
            cr, uid, [('model', '=', model_name)])

        new_line_id = self.pool.get('distribution.list.line').create(
            cr, uid, {'name': name,
                      'domain': domain,
                      'src_model_id': model_id[0],
                      })
        line_ids = [[4, new_line_id]]
        distribution_list = wizard[0].distribution_list_id

        if wizard[0].exclude:
            vals = {'to_exclude_distribution_list_line_ids': line_ids}
        else:
            vals = {'to_include_distribution_list_line_ids': line_ids}
        self.pool.get('distribution.list').write(
            cr, uid, distribution_list.id, vals, context=context)
