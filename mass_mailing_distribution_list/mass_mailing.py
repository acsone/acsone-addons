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

MSG_OK = "<p>Unsubscribe done successfully.</p>"
MSG_KO = "<p>The link you use to unsubscribe is no longer operational.<br/>" +\
    "Have you perhaps already unsubscribed?<br/>In any case, please " +\
    "use the link available in the next email.</p>"


class MassMailing(orm.Model):

    _inherit = 'mail.mass_mailing'

    _columns = {
        'distribution_list_id': fields.many2one('distribution.list',
                                                'Distribution List')
    }

    def on_change_model_and_list(self, cr, uid, ids, mailing_model, list_ids,
                                 context=None):
        res = super(MassMailing, self).on_change_model_and_list(
            cr, uid, ids, mailing_model, list_ids, context=context)
        res['value']['distribution_list_id'] = False

        return res

    def try_update_opt(self, cr, uid, mailing_id, res_id, context=None):
        '''
        Try to find a distribution list and call `update_opt` with the passed
        `res_id` as `partner_id`
        '''
        mailing_ids = self.exists(
            cr, uid, [mailing_id], context=context)
        if mailing_ids:
            mailing = self.browse(cr, uid, mailing_ids[0], context=context)
            dl = mailing.distribution_list_id or False
            if dl and res_id:
                already_opt_out = [p.id for p in dl.opt_out_ids]
                if int(res_id) not in already_opt_out:
                    dl_obj = self.pool['distribution.list']
                    dl_obj.update_opt(
                        cr, uid, dl.id, [res_id], context=context)
                    return MSG_OK
        return MSG_KO
