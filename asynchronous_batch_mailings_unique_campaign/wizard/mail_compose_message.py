# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.model
    def _prepare_vals(self, vals):
        """
        if mass_mailing_name is into the vals then transform it into the
        mass_mailing_id in order to avoid multipe creation once the active_ids
        will be split
        """
        super(MailComposeMessage, self)._prepare_vals(vals)
        if vals.get('mass_mailing_name'):
            mass_mailing_id = self.env['mail.mass_mailing'].create({
                'name': vals.pop('mass_mailing_name')
            })
            vals['mass_mailing_id'] = mass_mailing_id.id
