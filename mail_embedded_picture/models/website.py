# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of html_widget_embedded_picture, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     html_widget_embedded_picture is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     html_widget_embedded_picture is distributed
#     in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with html_widget_embedded_picture.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# optional python-slugify import (https://github.com/un33k/python-slugify)
try:
    import slugify as slugify_lib
except ImportError:
    slugify_lib = None

import werkzeug
from openerp.osv import osv, fields


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


class ir_attachment(osv.osv):
    _inherit = "ir.attachment"

    def _website_url_get(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.type == 'url':
                result[attach.id] = attach.url
            else:
                result[attach.id] = urlplus('/website/image', {
                    'model': 'ir.attachment',
                    'field': 'datas',
                    'id': attach.id,
                    'max_width': 1024,
                    'max_height': 768,
                })
        return result

    _columns = {
        'website_url': fields.function(
            _website_url_get, string="Attachment URL", type='char')
    }

    def try_remove(self, cr, uid, ids, context=None):
        """ Removes a web-based image attachment if it is used by no view
        (template)

        Returns a dict mapping attachments which would not be removed (if any)
        mapped to the views preventing their removal
        """
        Views = self.pool['ir.ui.view']
        attachments_to_remove = []
        # views blocking removal of the attachment
        removal_blocked_by = {}

        for attachment in self.browse(cr, uid, ids, context=context):
            # in-document URLs are html-escaped, a straight search will not
            # find them
            url = werkzeug.utils.escape(attachment.website_url)
            ids = Views.search(
                cr, uid, [('arch', 'like', url)], context=context)

            if ids:
                removal_blocked_by[attachment.id] = Views.read(
                    cr, uid, ids, ['name'], context=context)
            else:
                attachments_to_remove.append(attachment.id)
        if attachments_to_remove:
            self.unlink(cr, uid, attachments_to_remove, context=context)
        return removal_blocked_by
