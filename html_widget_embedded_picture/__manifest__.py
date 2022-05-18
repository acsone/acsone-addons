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
{
    'name': 'Mail Html Widget Embedded Picture',
    'version': '8.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'https://github.com/acsone/acsone-addons',
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
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
    'auto_install': False,
}
