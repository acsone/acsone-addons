# -*- coding: utf-8 -*-
import cStringIO
import contextlib
import hashlib
import json
import logging
import os
import datetime

from sys import maxint

import psycopg2
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
from PIL import Image

import openerp
from openerp.osv import fields
from openerp.addons.website.models import website
from openerp.addons.web import http
from openerp.addons.web.http import request, LazyResponse

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

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
