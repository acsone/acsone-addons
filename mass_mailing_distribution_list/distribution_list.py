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
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _

MODE = ['in', 'out']


class distribution_list(orm.Model):

    _inherit = 'distribution.list'

    _columns = {
        'newsletter': fields.boolean('Newsletter'),
        'partner_path': fields.char('Partner Path'),
        'opt_out_ids': fields.many2many('res.partner',
                                        'distribution_list_res_partner_out',
                                        id1='distribution_list_id',
                                        id2='partner_id', string='Opt-out'),
        'opt_in_ids': fields.many2many('res.partner',
                                       'distribution_list_res_partner_in',
                                       id1='distribution_list_id',
                                       id2='partner_id', string='Opt-in'),
    }

    _defaults = {
        # default model is partner
        'partner_path': 'id',
    }

    def _register_hook(self, cr):
        """
        Call `_get_mailing_model` of `mail.mass_mailing` to set a `domain` on
        `dst_model_id` to keep consistency between resulting ids
        """
        super(distribution_list, self)._register_hook(cr)

        res = self.pool['mail.mass_mailing']._get_mailing_model(
            cr, SUPERUSER_ID)
        mass_mailing_models = []
        for model in res:
            mass_mailing_models.append(model[0])
        type(self).dst_model_id.domain = [('model', 'in', mass_mailing_models)]

    def get_ids_from_distribution_list(
            self, cr, uid, ids, safe_mode=True, context=None):
        '''
        manage opt in/out.
        If the distribution list are newsletter and also have a parther_path
        then
        * remove all res_ids that contains a partner id into the opt_out_ids
        * add to res_ids all partner id into the opt_in_ids
        '''
        res_ids = super(distribution_list, self).\
            get_ids_from_distribution_list(cr, uid, ids, safe_mode=safe_mode,
                                           context=context)
        for dl in self.browse(cr, uid, ids, context=context):
            if dl.newsletter and dl.partner_path:
                partner_path = dl.partner_path
                # manage opt result
                dl_obj = self.pool[dl.dst_model_id.model]

                # opt in
                partner_ids = [p.id for p in dl.opt_in_ids]
                in_ids = dl_obj.search(
                    cr, uid, [(partner_path, 'in', partner_ids)],
                    context=context)
                res_ids = list(set(res_ids + in_ids))

                # opt out
                partner_ids = [p.id for p in dl.opt_out_ids]
                not_opt_out_ids = dl_obj.search(
                    cr, uid, [(partner_path, 'not in', partner_ids)],
                    context=context)
                res_ids = list(set(res_ids) & set(not_opt_out_ids))

        return res_ids

    def update_opt(
            self, cr, uid, dl_id, partner_ids, mode='out', context=None):
        '''
        update the list of opt out/in
        :type dl_id: integer
        :param dl_id: id of distribution list
        :type partner_ids: list of integer
        :param partner_ids: list of partner's id
        :type mode: char
        :param mode: in or out depending if we want to add or remove partner
            from the list
        :rtype: boolean
        :rparam: True if distribution list is well updated. Otherwise False
        :except: except_orm if mode is not into the MODE list
        '''
        if mode not in MODE:
            raise orm.except_orm(
                _('Error'), _('Mode "%s" is Not Into The Accepted Value'))
        opt_val = []
        if partner_ids:
            if len(partner_ids) == 1:
                opt_val = [(4, partner_ids[0])]
            else:
                p_ids = []
                dl_rec = self.browse(cr, uid, dl_id, context=context)
                for l in eval('dl_rec.opt_%s_ids' % mode, {'dl_rec': dl_rec}):
                    p_ids.append(l.id)
                opt_val = [(6, 0, list(set(partner_ids+p_ids)))]
            vals = {
                'opt_%s_ids' % mode: opt_val,
            }
            return self.write(cr, uid, dl_id, vals, context=context)

        return False
