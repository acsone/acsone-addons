# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of workflow_task,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     workflow_task is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     workflow_task is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with workflow_task.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Workflow tasks",

    'summary': """
        Automatically create tasks related to workflow activities""",

    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",

    'category': 'Technical Settings',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/wkf_activity.xml',
    ],
    'demo': [
        # 'demo.xml',
    ],
}
