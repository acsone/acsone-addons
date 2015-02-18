# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of email_separator, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     email_separator is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     email_separator is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with email_separator.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re

from openerp.addons.mail.mail_thread import decode_header
from openerp.osv import orm

BOUNCE_EXPR = '\+(\d+)-?([\w.]+)?-?(\d+)?'


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
            bounce_re = re.compile('%s%s' % (re.escape(bounce_alias),
                                             re.UNICODE), BOUNCE_EXPR)
            if bounce_re:
                message.set_param('To', message['To'].replace('+', '-', 1))

        return super(MailThread, self).message_route_check_bounce(
            cr, uid, message, context=context)
