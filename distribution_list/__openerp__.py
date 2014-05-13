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
    'name': 'Distribution List',
    'version': '1.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'base',
        'web',
        'email_template',
    ],
    'description': """
Distribution List
=================
This module provide features to allow the user to
* create distribution lists
* manage those distribution lists by adding or deleting lines
    """,
    'images': [
        'static/src/img/icons/gtk-ey.png',
    ],
    'data': [
        'security/distribution_list_security.xml',
        'security/ir.model.access.csv',
        'distribution_list_view.xml',
        'wizard/distribution_list_add_filter_view.xml',
        'wizard/mail_compose_message_view.xml',
        'wizard/merge_distribution_list_view.xml',
        'data/email_template_data.xml',
    ],
    'js': [
       'static/src/js/filter_selection.js',
    ],
    'qweb': [
       'static/src/xml/filter_selection.xml',
    ],
    'css': [
        'static/src/css/oe_save_only.css',
    ],
    'demo': [
        'demo/distribution_list_demo.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
