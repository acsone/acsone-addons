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


class MailComposeMessage(orm.TransientModel):
    _inherit = 'mail.compose.message'

    _columns = {
        'distribution_list_id': fields.many2one(
            'distribution.list', 'Distribution List'),
    }

    def create(self, cr, uid, vals, context=None):
        """
        This override allows the user to force the mass mail to
        the distribution list even if the header check-box was checked
        """
        if context is None:
            context = {}
        if 'distribution_list_id' in vals:
            if 'active_domain' in context:
                context = dict(context, {
                    'mail.compose.message.mode': 'mass_mail',
                })
                del(context['active_domain'])
                if 'use_active_domain' in vals:
                    vals['use_active_domain'] = False
        return super(MailComposeMessage, self).create(
            cr, uid, vals, context=context)

    def get_distribution_list_ids(self, cr, uid, distribution_list_ids,
                                  context=None):
        """
        return the resulting ids of distribution lists

        :type distribution_list_ids: [integer]
        :param distribution_list_ids: ids of distribution list
        """
        dl_obj = self.pool['distribution.list']
        return dl_obj.get_complex_distribution_list_ids(
            cr, uid, distribution_list_ids, context=context)

    def send_mail(self, cr, uid, ids, context=None):
        """
        overriding of send mail: it has to compute the ids
        of the distribution list to send mail.
        """
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.distribution_list_id and \
                not context.get('dl_computed', False):
            res_ids, _ = self.get_distribution_list_ids(
                cr, uid, [wizard.distribution_list_id.id], context=context)
            context = dict(context, active_ids=res_ids)
            # do not send mail to an empty list of recipients
            ids = res_ids and ids or []
        return super(MailComposeMessage, self).send_mail(
            cr, uid, ids, context=context)
