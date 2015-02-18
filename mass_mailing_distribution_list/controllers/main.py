# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mass_mailing_distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mass_mailing_distribution_list is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mass_mailing_distribution_list is distributed
#     in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mass_mailing_distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
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
