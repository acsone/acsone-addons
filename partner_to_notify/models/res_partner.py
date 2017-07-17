# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def _notify(self, message, force_send=False, send_after_commit=True,
                user_signature=True):
        partners_to_notify = self.env.context.get('partners_to_notify')
        if partners_to_notify:
            self = self.browse(partners_to_notify)
        return super(ResPartner, self)._notify(
            message, force_send=force_send,
            send_after_commit=send_after_commit, user_signature=user_signature)
