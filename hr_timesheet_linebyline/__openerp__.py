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
    "name": "HR Timesheet Line-by-Line",
    "version": "1.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [
        "images/hr_timesheet_linebyline.jpeg",
    ],
    "category": "Human Resources",
    "complexity": "easy",
    "depends": [
        "hr_timesheet",
        "hr_timesheet_sheet",
        "hr_timesheet_invoice",
        "project",
        "hr_timesheet_task", # hr_timesheet_task is from c2c-addons, it is incompatible with project_timesheet
        "account_analytic_project_id",
    ],
    "description": """
!!! THIS MODULE IS NOT YET MIGRATED !!!

HR Timesheet Line-by-Line
=========================

This module provides a simplified timesheet view for service companies.

It has the following features:
 * the attendence-related fields are hidden in the timesheet form
 * all lines of a week can be entered in a single list
   (instead of the default day by day view)
 * inherited from the c2c hr_timesheet_task module, it adds the task field
   in the timesheet view, allowing to select tasks directly when entering timesheets,
   (instead of the default which requires opening tasks to enter time)
 * the to_invoice field is hidden, and automatically set from the analytic account
   when the timesheet is confirmed (the rationale being that normal users do not
   decide themselves if their hours need to be invoiced or not)
 * when changing the start date of the timesheet, a sensible default is proposed
   for the end date
 * remake visible the user_id field in the timesheet lines table in the task view
""",
    "data" : [
        "hr_timesheet_linebyline_view.xml",
        "hr_analytic_timesheet_view.xml",
        "project_task_view.xml",
    ],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": False,
    "auto_install": False,
    "application": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

