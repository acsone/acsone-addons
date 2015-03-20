# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_europass, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_europass is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     hr_europass is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with hr_europass.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    def _get_default_attachment_ids(self):
        """
        Set the attachment of the CV model as default attachment of the
        mail composer
        """
        cv_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        cv_obj = self.env['hr.europass.cv']
        res = [[4, False]]
        if cv_id and active_model == cv_obj._name:
            cv = cv_obj.browse(cv_id)
            res = [[4, cv.attachment_id.id]]
        return res

    attachment_ids = fields.Many2many(default=_get_default_attachment_ids)
