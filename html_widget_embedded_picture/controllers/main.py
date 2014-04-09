# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan & Mignon Laurent
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
# -*- coding: utf-8 -*-
import cStringIO
import hashlib
import json
import logging
import datetime

from sys import maxint

import werkzeug.wrappers
from PIL import Image

import openerp
from openerp.addons.web import http
from openerp.addons.web.http import request

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)


class EmbeddedPicture(openerp.addons.web.controllers.main.Home):

    @http.route('/embedded/gen_img', type='http', auth='user', methods=['POST'])
    def gen_img(self, func, upload):
        img_tag = message = None
        try:
            image_data = upload.read()
            image = Image.open(cStringIO.StringIO(image_data))
            w, h = image.size
            if w * h > 42e6:  # Nokia Lumia 1020 photo resolution
                raise ValueError(
                    u"Image size excessive, uploaded images must be smaller "
                    u"than 42 million pixel")

            Attachments = request.registry['ir.attachment']
            attachment_id = Attachments.create(request.cr, request.uid, {
                'name': upload.filename,
                'datas': image_data.encode('base64'),
                'datas_fname': upload.filename,
                'res_model': 'ir.ui.view',
            }, request.context)

            [attachment] = Attachments.read(
                request.cr, request.uid, [attachment_id], ['website_url'],
                context=request.context)
            url = attachment['website_url']
        except Exception, e:
            logger.exception("Failed to upload image to attachment")
            message = unicode(e)

        return """<script type='text/javascript'>
            window.parent['%s'](%s, %s);
        </script>""" % (func, json.dumps(url), json.dumps(message))

    @http.route([
        '/website/image',
        '/website/image/<model>/<id>/<field>'
        ], auth="public", website=True)
    def website_image(self, model, id, field, max_width=maxint, max_height=maxint):
        Model = request.registry[model]

        response = werkzeug.wrappers.Response()

        id = int(id)

        ids = Model.search(request.cr, request.uid,
                           [('id', '=', id)], context=request.context) \
            or Model.search(request.cr, openerp.SUPERUSER_ID,
                            [('id', '=', id), ('website_published', '=', True)], context=request.context)

        if not ids:
            return self.placeholder(response)

        concurrency = '__last_update'
        [record] = Model.read(request.cr, openerp.SUPERUSER_ID, [id],
                              [concurrency, field], context=request.context)

        if concurrency in record:
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            try:
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format + '.%f')
            except ValueError:
                # just in case we have a timestamp without microseconds
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format)

        # Field does not exist on model or field set to False
        if not record.get(field):
            # FIXME: maybe a field which does not exist should be a 404?
            return self.placeholder(response)

        response.set_etag(hashlib.sha1(record[field]).hexdigest())
        response.make_conditional(request.httprequest)

        # conditional request match
        if response.status_code == 304:
            return response

        data = record[field].decode('base64')
        fit = int(max_width), int(max_height)

        buf = cStringIO.StringIO(data)

        image = Image.open(buf)
        image.load()
        response.mimetype = Image.MIME[image.format]

        w, h = image.size
        max_w, max_h = fit

        if w < max_w and h < max_h:
            response.data = data
        else:
            image.thumbnail(fit, Image.ANTIALIAS)
            image.save(response.stream, image.format)
            # invalidate content-length computed by make_conditional as writing
            # to response.stream does not do it (as of werkzeug 0.9.3)
            del response.headers['Content-Length']

        return response

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
