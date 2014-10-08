# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
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
from openerp import http, SUPERUSER_ID
from openerp.http import request


class MassMailController(http.Controller):

    @http.route(['/mail/newsletter/<int:mailing_id>/unsubscribe'],
                type='http', auth='none')
    def newsletter(self, mailing_id, email=None, res_id=None, **post):
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        mml_obj = request.registry['mail.mass_mailing']
        return mml_obj.try_update_opt(
            cr, uid, mailing_id, res_id, context=context)
