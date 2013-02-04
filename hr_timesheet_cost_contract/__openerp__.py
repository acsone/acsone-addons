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
    "name": "HR Timesheet cost based on contract",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [],
    "category": "Generic Modules/Human Resources",
    "complexity": "easy",
    "depends": ["hr_contract_wage_type","hr_timesheet_sheet"],
    "description": """

HR Timesheet cost based on contract
===================================

Compute the cost of an employee for his timesheets according
to his contract definitions. The effective cost is calculated when
timesheet is 'Confirmed'. If no contract are defined, an exception
is raised. 

This module is inspired from extra-trunk/hr_contract_timesheet that
updates the cost each time the unit_amount is changed but does
not warn if no contract exists.

Other known similar module:
    * extra-trunk/project_timesheet_contract relies on project.task.work

What we do here:
    * update the cost when the timesheet is confirmed (i.e. submitted)
    * prevent submission if no contract exists for the corresponding date
""",
    "data": [],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

