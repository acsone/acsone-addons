# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Jonathan Nemry & USER
# Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{

    "name" : "HR Europass",
    "category" : "Human Resources",
    "version" : "1.0",
    "depends" : ["base", "hr"],
    "author" : "Nemry Jonathan",

    "description" : """
HR Europass
===========

This application enables you to manage CV.
The format managed is the xml format Europass.

Features:
---------
* Upload CV
  * Create it,
  *	Update it.
* Search on CV content
* Send a CV by Email
* Automatically upload CV in Open ERP with a CV sent to "hrEuropass@gmail.com"
    """,
    'depends': [
        'hr_recruitment',
    ],
    'external_dependencies': {
        'python': ['pdfminer'],
    },
    'data' : [
        'security/hr_europass_security.xml',
        'security/ir.model.access.csv',
        'wizard/send_mail_view.xml',
        'hr_europass_view.xml',
        'hr_europass_workflow.xml',
    ],
    'demo' : [
    ],

    'update_xml' : [
    ],

    'test' : [
        'test/hr_europass_test.yml',
    ],
    'css':[
           'static/src/css/field_binary_css.css',
    ],
    'images':[
        'static/src/img/icons/db.png',
    ],
    'installable' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
