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
{
    'name': 'Mail HTML Widget Template',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Extra Tools',
    'depends': [
        'base',
        'web',
        'email_template',
    ],
    'description': """
Mail HTML Widget Template
=========================
This module allow to immediately manage placeholder from the mail composer
This tools is available on each html widget of Odoo

* Primary dropdownlist is filled with expected fields of the object \
    associated to the template.

* When choosing a field in a dropdownlist, two possibilities:

    * If the selected field is a relation to another object, an additional \
    dropdownlist filled with the expected fields of this object is append \
    to the toolbar (this generic mechanism follows relations between \
    objects through the data model and is intended for an undefined \
    number of levels)

    * Otherwise the placeholder is inserted into textarea
    """,
    'images': [],
    'data': [
        'views/mail_html_widget_template_view.xml',
    ],
    'qweb': [
        "static/src/xml/mail_html_widget_template.xml",
    ],
    'css': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
