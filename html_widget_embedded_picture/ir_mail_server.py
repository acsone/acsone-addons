# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan & Laurent Mignon
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
import lxml.html as html
from openerp.osv import orm
import re
from email.mime.image import MIMEImage
from uuid import uuid4


class ir_mail_server(orm.Model):

    _inherit = "ir.mail_server"

    def embedd_ir_attachment(self, cr, uid, message, body_part, context=None):
        html_str = body_part.get_payload(decode=True)
        root = html.document_fromstring(html_str)
        matching_buffer = {}
        for child in root.iter():
            # have to replace src by cid of the future attachement
            if child.tag == 'img':
                cid = uuid4()
                cid_id = ''.join('%s' % cid)
                matches = re.search('(id=)[\d]*', child.attrib.get('src'))
                if matches:
                    img_id = matches.group(0).split('=')[1]
                    matching_buffer[img_id] = cid_id
                    child.attrib['src'] = "cid:%s" % cid_id
        del body_part["Content-Transfer-Encoding"]
        body_part.set_payload(html.tostring(root))
        img_attachments = self.pool.get('ir.attachment').browse(cr, uid, map(int, matching_buffer.keys()))
        for img in img_attachments:
            content_id = matching_buffer.get("%s" % img.id)
            #our img.datas is already base64
            part = MIMEImage(img.datas, _encoder=lambda a: a, _subtype=img.datas_fname.split(".")[-1].lower(), )
            part.add_header('Content-Disposition', 'inline', filename=img.datas_fname)
            part.add_header('X-Attachment-Id', content_id)
            part.add_header('Content-ID', '<%s>' % content_id)
            part.add_header("Content-Transfer-Encoding", "base64")
            message.attach(part)
        return

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):
        for part in message.walk():
            if part.get_content_subtype() == 'html':
                self.embedd_ir_attachment(cr, uid, message, body_part=part, context=context)
                break
        super(ir_mail_server, self).send_email(cr, uid, message, mail_server_id=mail_server_id, smtp_server=smtp_server, smtp_port=smtp_port,
                   smtp_user=smtp_user, smtp_password=smtp_password, smtp_encryption=smtp_encryption, smtp_debug=smtp_debug,
                   context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
