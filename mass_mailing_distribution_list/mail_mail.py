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

import urllib
import urlparse

from openerp.osv import orm


class MailMail(orm.Model):

    _inherit = 'mail.mail'

    def _get_unsubscribe_url(
            self, cr, uid, mail, email_to, msg=None, context=None):
        '''
        Override native method to manage unsubscribe URL for distribution list
        case of newsletter.
        '''
        mml = mail.mailing_id
        if mml.distribution_list_id and mml.distribution_list_id.newsletter:
            res_id = mail.res_id
            if mail.model != 'res.partner':
                mail_obj = self.pool[mail.model]
                partner_path = mml.distribution_list_id.partner_path
                if partner_path in mail_obj._columns.keys():
                    curr_obj = self.pool[mail.model]
                    p_val = curr_obj.read(
                        cr, uid, res_id, [partner_path], context=context)
                    # get partner_id
                    res_id = p_val[partner_path][0]
                else:
                    # do not set URL for newsletter if no partner_id
                    return False
            param_obj = self.pool['ir.config_parameter']
            base_url = param_obj.get_param(
                cr, uid, 'web.base.url')
            vals = {
                'db': cr.dbname,
                'res_id': res_id,
                'email': email_to,
            }
            url = urlparse.urljoin(
                base_url, 'mail/newsletter/%(mailing_id)s/'
                          'unsubscribe?%(params)s' % {
                              'mailing_id': mail.mailing_id.id,
                              'params': urllib.urlencode(vals)
                          }
            )
            return '<small><a href="%s">%s</a></small>' % (
                url, msg or 'Click to unsubscribe')
        else:
            return super(MailMail, self)._get_unsubscribe_url(
                cr, uid, mail, email_to, msg=msg, context=context)
