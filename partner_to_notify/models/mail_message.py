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
            values['partner_ids'] = [(6, 0, partners_to_notify)]
        return super(MailMessage, self).create(values)

    @api.multi
    def write(self, values):
        partners_to_notify = self.env.context.get('partners_to_notify')
        if partners_to_notify and values.get('needaction_partner_ids'):
            values['needaction_partner_ids'] = [(6, 0, partners_to_notify)]
        return super(MailMessage, self).write(values)
