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

import re

from openerp.osv import orm
from openerp.addons.mail.mail_thread import decode_header


class MailThread(orm.AbstractModel):

    _inherit = 'mail.thread'

    def message_route_check_bounce(self, cr, uid, message, context=None):
        """
        Check bounce with a '+' case of any match then
        replace it with '-' before and call before
        """
        bounce_alias = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'mail.bounce.alias', context=context)
        email_to = decode_header(message, 'To')

        if bounce_alias in email_to:
            # Is a bounce ? Reuse the same technic as in super method in
            # mass_mailing/models/mail_thread.py
            bounce_re = re.compile(
                r'%s\+(\d+)-?([\w.]+)?-?(\d+)?' % re.escape(bounce_alias),
                re.UNICODE)
            if bounce_re.search(email_to):
                # Replace the first occurrence of a plus sign in the
                # recipient address by a dash, e.g.:
                #    catchall-bounces+543-kremlin@vladimir-putin.ru
                # => catchall-bounces-543-kremlin@vladimir-putin.ru
                del message['To']
                message['To'] = email_to.replace(
                    '%s+' % bounce_alias, '%s-' % bounce_alias, 1)

        return super(MailThread, self).message_route_check_bounce(
            cr, uid, message, context=context)
