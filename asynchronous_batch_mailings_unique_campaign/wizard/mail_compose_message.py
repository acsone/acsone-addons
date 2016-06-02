# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.model
    def _prepare_vals(self, vals):
        """
        To avoid to create a mass mailing for each chunk to process, create
        a common mass mailing and provide its id in the dictionary
        replacing the original mass mailing name
        """
        super(MailComposeMessage, self)._prepare_vals(vals)
        if vals.get('mass_mailing_name') and not vals.get('mass_mailing_id'):
            no_auto_thread = vals.get('no_auto_thread')
            reply_to_mode = no_auto_thread and 'email' or 'thread'
            reply_to = no_auto_thread and vals.get('reply_to') or False
            values = {
                'mass_mailing_campaign_id':
                    vals.get('mass_mailing_campaign_id', False),
                'name': vals.pop('mass_mailing_name'),
                'template_id': vals.get('template_id', False),
                'state': 'done',
                'reply_to_mode': reply_to_mode,
                'reply_to': reply_to,
                'sent_date': fields.Datetime.now(),
                'body_html': vals.get('body'),
                'mailing_model': vals['model'],
                'mailing_domain': vals.get('active_domain', []),
            }
            mass_mailing_id = self.env['mail.mass_mailing'].create(values)
            vals['mass_mailing_id'] = mass_mailing_id.id
