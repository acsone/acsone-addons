# -*- coding: utf-8 -*-
##############################################################################
#
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
from datetime import date

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as format
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class event_event(models.Model):

    def _check_registrations(self, states):
        regs = self.registration_ids.filtered(
            lambda reg: reg.state in states)
        if not regs:
            raise Warning(_('Send Invitation Failed: no Registrations '
                            'Concerned'))
        return True

    def _mass_mailing_action(self, template, mailing, domain=False):
        '''
        Create or Update mailing with template values
        :rtype[0]: Boolean
        :rparam[0]: True If mailing is created otherwise False
        :rtype[1]: mail.mass_mailing object
        :rparam[1]: mailing
        '''
        create = False
        if template:
            vals = {
                'body_html': template.body_html,
                'name': template.subject,
                'email_from': template.email_from,
            }
            if mailing:
                mailing.write(vals)
            else:
                vals['mailing_model'] = 'event.registration'
                vals['reply_to_mode'] = 'thread'
                domains = [('event_id', '=', self.id)]
                if domain:
                    domains.append(domain)
                vals['mailing_domain'] = str(domains)
                mailing = mailing.create(vals)
                create = True
            mailing.send_mail()

        return create, mailing

    _inherit = "event.event"

    # invitation
    invitation_template_id = fields.Many2one(
        'email.template', string='Invitation Template',
        select=True, track_visibility='onchange')
    invite_mass_mailing_id = fields.Many2one(
        'mail.mass_mailing', string='Mass Mailing Invitation',
        select=True, track_visibility='onchange')
    invitation_date = fields.Datetime(string="Invitation Date")

    # confirmation
    confirm_mass_mailing_id = fields.Many2one(
        'mail.mass_mailing', string='Mass Mailing Confirmation',
        select=True, track_visibility='onchange')
    confirmation_date = fields.Datetime(string="Confirmation Date")

    # cancellation
    cancel_mass_mailing_id = fields.Many2one(
        'mail.mass_mailing', string='Mass Mailing Cancellation',
        select=True, track_visibility='onchange')
    cancellation_template_id = fields.Many2one(
        'email.template', string='Cancellation Template',
        select=True, track_visibility='onchange')
    cancellation_date = fields.Datetime(string="Cancellation Date")

    @api.one
    def button_send_invitation(self):
        '''
        Send an invitation to event registration with `invite_mass_mailing_id`
        and apply template data to mass_mailing
        '''
        self._check_registrations(['draft'])
        domain = ('state', '=', 'draft')
        create, mailing = self._mass_mailing_action(
            self.invitation_template_id, self.invite_mass_mailing_id, domain)
        if create:
            self.invite_mass_mailing_id = mailing
        self.invitation_date = date.today().strftime(format)

    @api.one
    def confirm_event(self):
        self._check_registrations(['open'])
        domain = ('state', 'not in', ['draft', 'cancel'])
        create, mailing = self._mass_mailing_action(
            self.email_confirmation_id, self.confirm_mass_mailing_id, domain)
        if create:
            self.confirm_mass_mailing_id = mailing
        self.confirmation_date = date.today().strftime(format)

    @api.one
    def button_cancel(self):
        self._check_registrations(
            [c[0] for c in self.registration_ids._columns['state'].selection])
        res = super(event_event, self).button_cancel()
        create, mailing = self._mass_mailing_action(
            self.cancellation_template_id, self.cancel_mass_mailing_id)
        if create:
            self.cancel_mass_mailing_id = mailing
        self.cancellation_date = date.today().strftime(format)
        return res


class event_registration(models.Model):

    _inherit = "event.registration"
    _mail_mass_mailing = 'Event Registration'

    @api.one
    def registration_open(self):
        if not self.event_id.email_registration_id:
            raise Warning(_('Event Template is Required to Confirm '
                            'Registrations.'))
        return super(event_registration, self).registration_open()
