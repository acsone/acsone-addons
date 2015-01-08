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
{
    'name': 'Mail Html Widget Embedded Picture',
    'version': '1.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Html Widget',
    'depends': [
        'base',
        'web',
    ],
    'description': """
Mail Html Widget Embedded Picture
=================================
The module includes the images of type 'ir.attachment' referenced in the body
of the email as part of the muli-part email. As a result, the mail no longer
contains html link to Odoo. The integration of images is made at when the
server sends the email to conserve disk space.
""",
    'images': [
    ],
    'data': [
    ],
    'js': [
        'static/src/js/mail_html_widget_embedded_picture.js'
    ],
    'qweb': [
        'static/src/xml/mail_html_widget_embedded_picture.xml'
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
