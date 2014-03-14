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
import cStringIO
import json
import logging
from PIL import Image

import openerp
from openerp.addons.web import http

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
            if w*h > 42e6: # Nokia Lumia 1020 photo resolution
                raise ValueError(
                    u"Image size excessive, uploaded images must be smaller "
                    u"than 42 million pixel")

            data_uri = image_data.encode('base64').replace('\n', '')
            ext = upload.filename.split('.')[-1].lower()
            img_tag = '<img src="data:image/{0};base64,{1}">'.format(ext, data_uri)
        except Exception, e:
            logger.exception("Failed to upload image to attachment")
            message = unicode(e)

        return """<script type='text/javascript'>
            window.parent['%s'](%s, %s);
        </script>""" % (func, json.dumps(img_tag), json.dumps(message))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
