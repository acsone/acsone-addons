# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of project_member_ext,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     project_member_ext is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     project_member_ext is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with project_member_ext.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "project_member_ext",

    'summary': """
        Assign/Unassing projet's members recursively""",
    'author': 'ACSONE SA/NV,',
    'website': "http://acsone.eu",
    'category': 'Project Management',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'project',
    ],
}
