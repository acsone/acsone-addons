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
from openerp.osv import orm


class MailComposeMessage(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def create(self, cr, uid, vals, context=None):
        """
        :type vals: {}
        :param vals: if vals contains `mass_mailing_id` then check if the
            `mail.mass_mailing` has a `distribution_list_id`
            If it has then add it into the `vals`
        :rparam: super()
        """
        if context is None:
            context = {}
        if vals.get('mass_mailing_id', False):
            mass_mailing_rec = self.pool['mail.mass_mailing'].browse(
                cr, uid, vals['mass_mailing_id'], context=context)
            if mass_mailing_rec.distribution_list_id:
                vals['distribution_list_id'] =\
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
