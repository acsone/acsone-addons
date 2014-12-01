# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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
