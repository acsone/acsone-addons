# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mass_mailing_distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mass_mailing_distribution_list is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mass_mailing_distribution_list is distributed
#     in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mass_mailing_distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class merge_distribution_list(orm.TransientModel):

    _inherit = 'merge.distribution.list'

    def _is_newsletter(self, cr, uid, context=None):
        """
        :rtype: boolean
        :rparam: True if dl active_ids are newsletter, otherwise False
        """
        context = context or {}
        if context.get('active_ids'):
            active_ids = context.get('active_ids')
            return all([dl.newsletter for dl in self.pool['distribution.list'].
                        browse(cr, uid, active_ids, context=context)])
        return False

    _columns = {
        'is_newsletter': fields.boolean('is_newsletter'),
    }

    _defaults = {
        'is_newsletter': lambda self, cr, uid, context=None:
            self._is_newsletter(cr, uid, context=context)
    }
