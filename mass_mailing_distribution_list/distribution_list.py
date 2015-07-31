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

import logging
import base64
import re

import openerp
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

MODE = ['in', 'out']
TEST_MSG = openerp.tools.ustr('TEST')

MATCH_EMAIL = re.compile('<(.*)>', re.IGNORECASE)


class distribution_list(orm.Model):

    _name = 'distribution.list'
    _inherit = ['distribution.list', 'mail.thread']

    def _set_active_ids(self, cr, uid, dl_id, msg, context):
        """
        Verify that email_from identifies uniquely a document
        in the target model of the distribution list
        If True:
        * Set `dl_computed` to True together with `active_ids` indicating
          the distribution should not be computed, this is only a test message
          to forward to the sender, in this case the "TEST" prefix of
          the subject is also removed
        * Set `dl_computed` to False indicating the distribution
          must be computed, the mail will be sent to all distribution list
          recipients
        :type dl_id: integer
        :param dl_id: distribution list id
        :type msg: {}
        :param msg: mail unicode values email_from, subject...
        :type context: {}
        :param context: context in which to set `active_ids` and `dl_computed`
        """
        res_ids = self._get_mailing_object(
            cr, uid, dl_id, msg['email_from'], context=context)
        if len(res_ids) != 1:
            _logger.warning(
                'The Unknown or Ambiguous Email Address (%s) '
                'tries to use the Distribution List to forward a Mail' %
                msg['email_from'])
        elif msg['subject'][0:4].upper() == TEST_MSG:
            # do not send to all recipients: this is just a test
            msg['subject'] = msg['subject'][4:]
            context['active_ids'] = res_ids
            context['dl_computed'] = True
        else:
            context['dl_computed'] = False

    def _get_mailing_object(
            self, cr, uid, dl_id, email_from, mailing_model=False,
            email_field='email', context=None):
        """
        :type email_from: char
        :param email_from: email to find
        :type mailing_model: char
        :param mailing_model: a given model name to search on
        :type email_field: char
        :param email_field: name of the columns that possibly contains the
            email to search
        :rtype: integer or boolean
        :rparam: id of the object that contains `email_from` or False
        """
        res = re.findall(MATCH_EMAIL, email_from)
        email_from = res and res[0] or email_from

        if not mailing_model:
            dl = self.browse(cr, uid, dl_id, context=context)
            mailing_model = dl.dst_model_id.model

        mailing_object = self.pool[mailing_model]
        domain = [(email_field, '=', email_from)]

        mailing_ids = mailing_object.search(
            cr, uid, domain, context=context)
        return mailing_ids

    def _get_attachment_id(self, cr, uid, datas, context=None):
        ir_attach_vals = {
            'name': datas[0],
            'datas_fname': datas[0],
            'datas': base64.encodestring(datas[1]),
            'res_model': 'mail.compose.message',
        }
        return self.pool['ir.attachment'].create(
            cr, uid, ir_attach_vals, context=context)

    def _get_mail_compose_message_vals(
            self, cr, uid, msg, dl_id, mailing_model=False, context=None):
        dl = self.browse(cr, uid, dl_id, context=context)
        if not mailing_model:
            mailing_model = dl.dst_model_id.model

        attachment_ids = []
        if msg.get('attachments', False):
            for attachment in msg['attachments']:
                attachment_ids.append(self._get_attachment_id(
                    cr, uid, attachment, context=context))
        return {
            'email_from': msg.get('from', False),
            'composition_mode': 'mass_mail',
            'subject': msg.get('subject', False),
            'body': msg.get('body', False),
            'distribution_list_id': dl_id,
            'mass_mailing_name': 'Mass Mailing %s' % dl.name,
            'model': mailing_model,
            'attachment_ids': [[6, 0, attachment_ids]],
        }

    def _mail_alias_id_function(self, cr, uid, ids, name, args, context=None):
        """
        If `distributrion.list.mail_forwarding` is True then a mail.alias
        must be set for this distribution list. If there is no one then create
        a `mail.alias` based on the distribution list name.
        Keep current `mail_alias_id` for other cases.
        """
        result = {i: False for i in ids}
        for dl_vals in self.read(
                cr, uid, ids, ['mail_forwarding', 'mail_alias_id', 'name'],
                context=context):
            if dl_vals['mail_forwarding'] and not dl_vals['mail_alias_id']:
                result[dl_vals['id']] = self.generate_alias(
                    cr, uid, dl_vals['id'], dl_vals['name'], context=context)
            else:
                # For all other cases keep the current value
                result[dl_vals['id']] = dl_vals['mail_alias_id'] and\
                    dl_vals['mail_alias_id'][0] or False

        return result

    _mail_alias_id_triggers = {
        'distribution.list': (lambda self, cr, uid, ids, context=None: ids,
                              ['mail_forwarding'], 10),
    }

    _columns = {
        'mail_forwarding': fields.boolean('Mail Forwarding'),
        'mail_alias_id': fields.function(
            _mail_alias_id_function, type='many2one', relation='mail.alias',
            string='Mail Alias', store=_mail_alias_id_triggers),

        'newsletter': fields.boolean('Newsletter'),
        'partner_path': fields.char('Partner Path'),
        'opt_out_ids': fields.many2many('res.partner',
                                        'distribution_list_res_partner_out',
                                        id1='distribution_list_id',
                                        id2='partner_id', string='Opt-Out'),
        'opt_in_ids': fields.many2many('res.partner',
                                       'distribution_list_res_partner_in',
                                       id1='distribution_list_id',
                                       id2='partner_id', string='Opt-In'),
    }

    _defaults = {
        # default model is partner
        'partner_path': 'id',
    }

    def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        """
        Override the native mail.thread method to not create a document anymore
        for distribution list object.
        New Behavior is to forward the current message `msg_dict` to all
        recipients of the distribution list
        :type custom_values: {}
        :param custom_values: contains the distribution list id into key 'id'
        :type msg_dict: {}
        :param msg_dict: message to forward to all resulting ids of
            distribution list
        """
        dl_id = None
        if custom_values is None:
            custom_values = {}
        if not custom_values.get('distribution_list_id'):
            _logger.warning('Alias %s ' % msg_dict.get('to', 'Not Specified') +
                            'Has no Distribution List into its '
                            '"custom_values": Please Specify One to Allow '
                            'Mail Forwarding')
        else:
            dl_id = custom_values['distribution_list_id']
            if self.allow_forwarding(cr, uid, dl_id, context=context):
                self.distribution_list_forwarding(
                    cr, uid, msg_dict, dl_id, context=context)
            else:
                _logger.warning('Email "%s" try to launch'
                                % msg_dict.get('email_from', False) +
                                ' mail forwarding on distribution list '
                                'with id "%s"' % dl_id)

        return dl_id

    def message_update(
            self, cr, uid, ids, msg_dict, update_vals=None, context=None):
        """
        Do not allow update case of mail forwarding
        """
        return True

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
                _('Error'), _('Mode "%s" is not a valid mode'))
        opt_val = []
        if partner_ids:
            if len(partner_ids) == 1:
                opt_val = [(4, partner_ids[0])]
            else:
                p_ids = []
                dl_rec = self.browse(cr, uid, dl_id, context=context)
                for l in eval('dl_rec.opt_%s_ids' % mode, {'dl_rec': dl_rec}):
                    p_ids.append(l.id)
                opt_val = [(6, 0, list(set(partner_ids + p_ids)))]
            vals = {
                'opt_%s_ids' % mode: opt_val,
            }
            return self.write(cr, uid, dl_id, vals, context=context)

        return False

    def generate_alias(self, cr, uid, dl_id, dl_name, context=None):
        """
        :type dl_name: char
        :param dl_name: name of a distribution list
        :rtype: integer
        :rparam: id a mail.alias object created from the given `dl_name`
        :raise orm_except: If there is no `catchall alias` then raise an error
        """
        alias_obj = self.pool['mail.alias']
        ir_cfg_obj = self.pool.get('ir.config_parameter')

        catchall_alias = ir_cfg_obj.get_param(
            cr, uid, 'mail.catchall.alias', context=context)
        if not catchall_alias:
            raise orm.except_orm(
                _('Error'),
                _('Please contact your Administrator '
                  'to configure a "catchall" email alias'))
        distribution_list_model_id = self.pool['ir.model'].search(
            cr, uid, [('model', '=', 'distribution.list')], limit=1)[0]
        vals = {
            'alias_name': '%s+%s' % (catchall_alias, dl_name),
            'alias_defaults': '{"distribution_list_id": %s}' % str(dl_id),
            'alias_model_id': distribution_list_model_id,
        }
        return alias_obj.create(cr, uid, vals, context=context)

    def distribution_list_forwarding(self, cr, uid, msg, dl_id, context=None):
        '''
        Create a `mail.compose.message` depending of the message msg and then
        send a mail with this composer to the resulting ids of the
        distribution list `dl_id`
        '''
        if context is None:
            context = {}
        ctx = context.copy()
        # update ctx['active_ids']
        self._set_active_ids(cr, uid, dl_id, msg, ctx)
        if ctx.get('active_ids') or not ctx.get('dl_computed', True):
            mail_composer_obj = self.pool['mail.compose.message']
            # get composer values to create wizard
            mail_composer_vals = self._get_mail_compose_message_vals(
                cr, uid, msg, dl_id, context=ctx)
            mail_composer_id = mail_composer_obj.create(
                cr, uid, mail_composer_vals, context=ctx)
            mail_composer_obj.send_mail(
                cr, uid, [mail_composer_id], context=ctx)

    def allow_forwarding(self, cr, uid, dl_id, context=None):
        """
        Define if the distribution list is allowed to make forwarding
        :type dl_id: integer
        :param dl_id: a distribution_list id
        :rtype: boolean
        :rparam: True if distribution is allowed otherwise False
        """
        return self.read(
            cr, uid, dl_id, ['mail_forwarding'],
            context=context)['mail_forwarding']
