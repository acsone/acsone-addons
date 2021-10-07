# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_analytic_invoice_note,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_analytic_invoice_note is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_analytic_invoice_note is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_analytic_invoice_note.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Account Analytic Invoice Note",

    'summary': """
        Add invoice note on analytic account.""",
    'author': 'ACSONE SA/NV',
    'website': "https://acsone.eu",
    'category': 'Accounting & Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'hr_timesheet_invoice',
    ],
    'data': [
        'views/account_analytic_account_view.xml',
    ],
    'pre_init_hook': 'move_fields',
    'installable': False,
}
