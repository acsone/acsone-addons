# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailMessage(models.Model):

    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        partners_to_notify = self.env.context.get('partners_to_notify')
        if partners_to_notify:
            partner_ids = values.get('partner_ids', [])
            for partner_id in partners_to_notify:
                partner_ids.append((4, partner_id))
            values['partner_ids'] = partner_ids
        return super(MailMessage, self).create(values)
