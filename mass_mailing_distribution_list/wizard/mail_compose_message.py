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

from openerp.osv import orm


class MailComposeMessage(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def create(self, cr, uid, vals, context=None):
        """
        If the composer is created from a mass mailing linked to
        a distribution list, add the list to the composer
        """
        if vals.get('mass_mailing_id', False):
            mass_mailing_rec = self.pool['mail.mass_mailing'].browse(
                cr, uid, vals['mass_mailing_id'], context=context)
            if mass_mailing_rec.distribution_list_id:
                vals['distribution_list_id'] = \
                    mass_mailing_rec.distribution_list_id.id
        return super(MailComposeMessage, self).create(cr, uid, vals,
                                                      context=context)

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """
        If result of super has a `mailing_id` and `wizard` has a
        `distribution_list_id` then write into this `mail.mass_mailing` the
        found `distribution_list_id`

        **Note**
        super() result is a {key: {}}
        `mailing_id` is common for all `key`
        """
        res = super(MailComposeMessage, self).get_mail_values(
            cr, uid, wizard, res_ids, context=context)
        if wizard.distribution_list_id:
            for v in res.values():
                if v.get('mailing_id', False):
                    vals = {
                        'distribution_list_id': wizard.distribution_list_id.id,
                    }
                    self.pool['mail.mass_mailing'].write(
                        cr, uid, [v['mailing_id']], vals, context=context)
                break
        return res
