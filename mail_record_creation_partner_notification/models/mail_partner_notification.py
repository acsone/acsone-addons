# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailPartnerNotification(models.AbstractModel):

    _name = 'mail.partner.notification.mixin'
    _description = 'Mail Partner Notification (Abstract)'

    _subscribe_notified_partner_on_creation = True

    @api.model
    def create(self, values):
        partners_to_notify = self.get_partners_to_notify_on_creation(values)
        if partners_to_notify:
            self = self.with_context(partners_to_notify=partners_to_notify.ids)
        record = super(MailPartnerNotification, self).create(values)
        record.subscribe_partners(partners_to_notify)
        return record

    @api.model
    def get_partners_to_notify_on_creation(self, values):
        """
        Inherit this method to get partners to notify when a record
        is created.
        :param values: creation values
        :return: recordset('res.partner')
        """
        return self.env['res.partner']

    @api.multi
    def subscribe_partners(
        self, partners,
        channel_ids=None, subtype_ids=None, force=None,
    ):
        self.ensure_one()
        if not self._subscribe_notified_partner_on_creation or not partners:
            return
        self.message_subscribe(
            partner_ids=partners.ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids,
            force=force,
        )
