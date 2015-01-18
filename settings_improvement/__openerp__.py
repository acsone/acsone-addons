# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of settings_improvements, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     settings_improvements is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     settings_improvements is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with settings_improvements.
#     If not, see <http://www.gnu.org/licenses/>.
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
        "ir_noupdate_override",
    ],
    "description": """
Settings Improvement
====================

This module improves some native administrations features.

Only improvements based on "base" can be included in this module.
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
        "workflow_view.xml",
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
