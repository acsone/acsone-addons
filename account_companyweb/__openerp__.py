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
    "name": "CompanyWeb.be",
    "version": "1.0",
    "author": "Adrien Peiffer - ACSONE SA/NV",
    "category":"Generic Modules/Accounting",
    "website": "http://www.acsone.eu",
    "depends":['base_vat','account_financial_report_webkit','account_accountant'],
    "description": """

CompanyWeb.be
===================================

This module provides access to the financial health of Belgian companies that are saved in your database from the client display.
All of the information are coming form companyweb BVBA/SPRL database therefore you must have a subscription to companyweb BVBA/SPRL to access to information

Main Features
-------------
* Provides information (Name, address, VAT number, credit limit, some financial informations like equity capital, health barometer, some warnings) about Belgian companies which are record your database
* Update data(address, credit limit) of company which are stored in your database with companyweb data 
* Allow to consult a commercial report about Belgian companies which are record your database on companyweb BVBA/SPRL website 
* Generate financial reports which must be provided to companyweb BVBA/SPRL

More information about companyweb BVBA/SPRL on http://www.companyweb.be
    """,
    "data": [
                "wizard/account_companyweb_report_wizard_view.xml",
                  "wizard/account_companyweb_wizard_view.xml",
                  "view/res_config_view.xml",
                  "view/res_partner_view.xml",
    ],
    "demo": [],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
