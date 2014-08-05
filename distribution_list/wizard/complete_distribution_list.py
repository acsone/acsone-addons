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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class merge_distribution_list(orm.TransientModel):

    _name = 'merge.distribution.list'
    _description = 'Complete Distribution List'

    _columns = {
        'distribution_list_id': fields.many2one('distribution.list', 'Distribution List to Complete', required=True),
    }

#public methods

    def merge_distribution_list(self, cr, uid, ids, context=None):
        """
        ==========================
        complete_distribution_list
        ==========================
        Call ``complete_distribution_list`` with distribution.list
        passing on hand the selected distribution list id and on the other the
        ids of the ``active_ids``
        :param context: key ``active_ids`` contains the ids of distribution that
                        will complete the selected distribution list of the wizard
        :raise orm.except_orm: If no ids into the value of ``active_ids`` or no key
                               ``active_ids`` into the context.
        """
        if len(context.get('active_ids', False) or []) == 0:
            raise orm.except_orm(_('Error'), _('At Least One Distribution List Must Be Selected'))
        src_dist_list_ids = []
        for wiz in self.browse(cr, uid, ids, context=context):
            src_dist_list_ids.append(wiz.distribution_list_id.id)
        self.pool['distribution.list'].complete_distribution_list(cr, uid, src_dist_list_ids, context['active_ids'], context=context)

