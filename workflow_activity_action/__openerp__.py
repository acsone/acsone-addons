# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of workflow_activity_action,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     workflow_activity_action is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     workflow_activity_action is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with workflow_activity_action.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Workflow activity action",

    'summary': """
        Manage object action from its activities""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Technical Settings',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'base_suspend_security',
    ],
    'data': [
        'views/wkf_activity.xml',
        'views/workflow_activity_action.xml',
    ],
    'qweb': [
        'static/src/xml/base.xml',
    ],
}
