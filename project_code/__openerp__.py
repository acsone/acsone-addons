# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Stéphane Bidoul & Olivier Laurent
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
    "name": "Project Code",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": ["images/screenshot1.png", "images/screenshot2.png"],
    "category": "Project Management",
    "complexity": "easy",
    "depends": ["project"],
    "description": """
!!! THIS MODULE IS NOT YET MIGRATED !!!

A module for companies who like to reference projects by their code.

It has the following features:
 * the project code is made visible on project views (form, tree, filter)
 * the project and analytic account names are displayed as "code - name" (name_get)
 * quick search on project and analytic account include code (name_search)
""",
    "data": ["project_view.xml"],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": False,
    "auto_install": False,
    "application": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

