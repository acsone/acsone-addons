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
    "name": "HR Contract Wage Type",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [
        "images/hr_contract_wage_type.jpeg",
        "images/hr_contract_hourly_wage.jpeg",
    ],
    "category": "Human Resources",
    "complexity": "easy",
    "depends": ["hr_contract"],
    "description": """
HR Contract Wage Type
=====================

Reintroduce wage_type and wage_type_period classes that were removed from the
OpenERP hr_contract official addon in 6.1.

These classes were present in 6.0 and removed in 6.1 following the
introduction of the hr_payroll module. However, hr_payroll does not provide
similar functionality and data cannot be migrated. This module restores
identical functionality.

Module introduces also the hourly wage of the employee on its contract.
This computed field remains invisible in screens but can be exported in CSV
files.
""",
    "data": [
        "hr_contract_wage_type_data.xml",
        "hr_contract_wage_type_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "test": [
        "test/hr_contract_wage_type_hourly_wage.yml",
    ],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
