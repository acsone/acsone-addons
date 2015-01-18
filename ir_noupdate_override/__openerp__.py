# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of ir_noupdate_override, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     ir_noupdate_override is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     ir_noupdate_override is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with ir_noupdate_override.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "ir_noupdate_override",

    'summary': """
        Override noupdate setting in addons.""",

    'description': """
        When installed, this module let developers
        create addons that override records that have
        been set noupdate=1.

        This is particularly useful to force the modification
        of default record rules by addons.
    """,

    'author': "ACSONE SA/NV",
    'website': "http://acsone.eu",
    'license': 'AGPL-3',

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base'],

    'data': [
    ],

    'demo': [
    ],
}
