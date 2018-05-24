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

import lxml.html as html
import re
from email.mime.image import MIMEImage
from uuid import uuid4
from email import Encoders

from openerp import tools
from openerp.osv import orm

IMAGE_FORMAT = ['png', 'jpg', 'jpeg', 'gif']
DEFAULT_FORMAT = 'png'


class ir_mail_server(orm.Model):

    _inherit = "ir.mail_server"

    def embedd_ir_attachment(self, cr, uid, message, body_part, context=None):
        # a unicode string is required here
        html_unicode_str = tools.ustr(body_part.get_payload(decode=True))
        root = html.document_fromstring(html_unicode_str)
        matching_buffer = {}
        for child in root.iter():
            # have to replace src by cid of the future attachement
            if child.tag == 'img':
                cid = uuid4()
                cid_id = ''.join('%s' % cid)
                matches = re.search(r'(ir.attachment\/)[\d]*',
                                    child.attrib.get('src'))
                if not matches:
                    matches = re.search(r'(id=)[\d]+', child.attrib.get('src'))
                if matches:
                    m_id = matches.group(0)
                    img_id = m_id.split('/')[1] if '=' not in m_id else\
                        m_id.split('=')[1]
                    if img_id:
                        matching_buffer[img_id] = cid_id
                        child.attrib['src'] = "cid:%s" % cid_id
        del body_part["Content-Transfer-Encoding"]
        # body has to be re-encoded into the message part using
        # the initial output charset
        body_part.set_payload(html.tostring(
            root, encoding=body_part.get_charset().get_output_charset()))
        Encoders.encode_base64(body_part)
        img_attachments = self.pool.get('ir.attachment').browse(
            cr, uid, map(int, matching_buffer.keys()))
        for img in img_attachments:
            content_id = matching_buffer.get("%s" % img.id)
            # our img.datas is already base64
            part = MIMEImage(img.datas, _encoder=lambda a: a,
                             _subtype=img.datas_fname.split(".")[-1].lower(), )
            data_fname = img.datas_fname
            accepted_format = DEFAULT_FORMAT
            for f_format in IMAGE_FORMAT:
                if data_fname[-len(f_format):] == f_format:
                    accepted_format = data_fname[-len(f_format):]
            part.add_header(
                'Content-Disposition', 'inline', filename=data_fname)
            part.add_header('X-Attachment-Id', content_id)
            part.add_header('Content-ID', '<%s>' % content_id)
            part.replace_header('Content-Type', 'image/%s' % accepted_format)
            part.add_header("Content-Transfer-Encoding", "base64")
            message.attach(part)
        return

    def send_email(
        self, cr, uid, message, mail_server_id=None, smtp_server=None,
        smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False, context=None):
        for part in message.walk():
            if part.get_content_subtype() == 'html':
                self.embedd_ir_attachment(
                    cr, uid, message, body_part=part, context=context)
                break
        return super(
            ir_mail_server, self).send_email(
                cr, uid, message, mail_server_id=mail_server_id,
                smtp_server=smtp_server, smtp_port=smtp_port,
                smtp_user=smtp_user, smtp_password=smtp_password,
                smtp_encryption=smtp_encryption, smtp_debug=smtp_debug,
                context=context)
