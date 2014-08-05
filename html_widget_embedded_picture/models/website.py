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
        'website_url': fields.function(_website_url_get, string="Attachment URL", type='char')
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
            ids = Views.search(cr, uid, [('arch', 'like', url)], context=context)

            if ids:
                removal_blocked_by[attachment.id] = Views.read(
                    cr, uid, ids, ['name'], context=context)
            else:
                attachments_to_remove.append(attachment.id)
        if attachments_to_remove:
            self.unlink(cr, uid, attachments_to_remove, context=context)
        return removal_blocked_by

