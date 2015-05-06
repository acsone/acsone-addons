# -*- coding: utf-8 -*-
##############################################################################
#
# This file is part of email_separator,
# an Odoo module.
#
# Authors: ACSONE SA/NV (<http://acsone.eu>)
#
# email_separator is free software:
# you can redistribute it and/or modify it under the terms of the GNU
# Affero General Public License as published by the Free Software
# Foundation,either version 3 of the License, or (at your option) any
# later version.
#
# email_separator is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with email_separator.
# If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class ir_mail_server(orm.Model):

    _inherit = 'ir.mail_server'

    def send_email(
            self, cr, uid, message, mail_server_id=None, smtp_server=None,
            smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False, context=None):
        bounce_alias = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'mail.bounce.alias', context=context)
        catchall_domain = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'mail.catchall.domain', context=context)
        rpath = message['Return-Path']
        if bounce_alias and catchall_domain and rpath:
            if '%s-' % bounce_alias in rpath.split('@', 1)[0]:
                # Replace the first dash occurrence in the "identity" part of
                # the return path (i.e. the bounce email address)
                # by a plus sign, e.g.:
                #    catchall-bounces-543-kremlin@vladimir-putin.ru
                # => catchall-bounces+543-kremlin@vladimir-putin.ru
                rpath = rpath.replace(
                    '%s-' % bounce_alias, '%s+' % bounce_alias, 1)
                del message['Return-Path']
                message['Return-Path'] = rpath

        return super(ir_mail_server, self).send_email(
            cr, uid, message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port, smtp_user=smtp_user,
            smtp_password=smtp_password, smtp_encryption=smtp_encryption,
            smtp_debug=smtp_debug, context=context)
