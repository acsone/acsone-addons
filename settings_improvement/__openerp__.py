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
    "name": "Settings Improvement",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [
    ],
    "category": "Other",
    "depends": [
        "base",
    ],
    "description": """
Settings Improvement
====================

This module improves some native administrations features.

Only improvements based on "base" can be included in this module.

Note: the flag "auto_install" is set to True hereafter, thus the module will be automatically installed each time a new DB will be created. To avoid
this principle, reset simply this flag to False.
""",
    "data": [
        "security/settings_improvement.xml",
        "base_menu.xml",
        "res_users_data.xml",
        "res_users_view.xml",
        "ir_ui_view_view.xml",
        "ir_actions.xml",
        "ir_ui_menu_view.xml",
        "ir_model.xml",
        "ir_translation_view.xml",
    ],
    "demo": [
    ],
    "test": [
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}


