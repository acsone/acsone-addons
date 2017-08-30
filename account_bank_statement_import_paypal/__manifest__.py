# -*- coding: utf-8 -*-
# Copyright 2014-2015 Akretion (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Import Paypal Bank Statements',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'summary': 'Import Paypal CSV files as Bank Statements in Odoo',
    'depends': ['account_bank_statement_import'],
    'external_dependencies': {'python': ['unicodecsv']},
    'data': [],
    'installable': True,
}
