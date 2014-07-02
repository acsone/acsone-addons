# -*- coding: utf-8 -*-
#
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    "name": "Companyweb",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "category": "Generic Modules/Accounting",
    "website": "http://www.acsone.eu",
    "depends": [
        'account_financial_report_webkit',
        'base_vat',
        # TODO: account voucher is required
        #       for the test suite only
        #       (need to refactor the test suite)
        'account_voucher',
    ],
    'external_dependencies': {
        'python': ['lxml', 'xlwt'],
    },
    "description": """
Companyweb - Know who you are dealing with
==========================================

This module provides access to financial health information about Belgian
companies right from the OpenERP Customer form. Information is obtained
from the Companyweb database (www.companyweb.be).

You must be a Companyweb customer to use this module in production.
Please visit www.companyweb.be and use login 'cwacsone',
with password 'demo' to obtain test credentials.

Main Features
-------------
* Obtain crucial information about Belgian companies,
  based on their VAT number: name, address,
  credit limit, health barometer, financial informations
  such as turnover or equity capital, and more.
* Update address and credit limit in your OpenERP database.
* Generate reports about payment habits of your customers.
* Access to detailed company information on www.companyweb.be.

Technical information
---------------------
This module depends on module account_financial_report_webkit which
provides an accurate algorithm for open invoices report.

Contributors
------------
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Adrien Peiffer
""",
    "data": [
        "wizard/account_companyweb_report_wizard_view.xml",
        "wizard/account_companyweb_wizard_view.xml",
        "view/res_config_view.xml",
        "view/res_partner_view.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
    "installable": True,
}
