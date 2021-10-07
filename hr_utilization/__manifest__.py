# -*- coding: utf-8 -*-
#
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
#

{
    "name": "HR Utilization Report",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "images": [
        "images/screenshot1.png",
        "images/screenshot2.png",
        "images/hr_utilization_report.jpeg",
    ],
    "category": "Human Resources",
    "complexity": "easy",
    "depends": ["hr_timesheet", "hr_contract", "report_webkit"],
    "description": """

HR Utilization Report
=====================

A module to produce a Utilization Table report.

A Utilization Table summarizes how employees spent time over a given period
and categories, as a percentage of the employee's full time schedule.

Each row correspond to an employee, and each column is a category.
Categories are fully configurable and typically have names such
Billable, Sales, Holidays, Sick, etc. A category is
defined as a set of analytic accounts, including their children accounts.

The report can also compute the number of full-time equivalent were active
in your company over any given period.

The hours used for the report come from timesheet lines, so it is of course
a prerequisite to have complete timesheets in order to produce meaningful
reports.

Follow the following steps to prepare and configure a report:
 * for each employee you want to include in the report, you need to have a
   Contract defined if Human Resources > Employees and associate a Working Time
   in the Working Schedule field (hours of employees with no contract or
   contract without a working schedule are printed in a separate section of
   the report);
 * in Settings > Companies, set the Working Time corresponding to a Full Time
   schedule on your company in the configuration tab;
 * in Settings > Technical > Resource, associate Resource
   Leaves corresponding to public holidays and other days your company is
   closed and associate these leaves to each Working Time;
 * in Human Resources > Configuration > Utilization, create columns (such as
   Billable, Sick, Holidays, etc) and link each column to the corresponding
   analytic accounts; children analytic accounts are included automatically,
   so if for instance your Billable projects are all under the same analytic
   account, you only need to include one;
 * in Human Resources > Configuration > Utilization, create a configuration
   listing all columns you want in your report; tick the 'With
   Full-time Equivalent Column' checkbox if you need the report to compute how
   many FTE you have over the period.

You can then print the report from Reporting > Human Resources > Utilization
Report, by selecting the configuration and the time period.

Caveats:
 * all analytic lines corresponding to timesheet lines must be in an analytic
   journal of type general (which is the OpenErp default);
 * the module currently assumes all timesheet lines quantities are in hours
   and does not attempt to verify if this assumption is valid.

The report is a webkit report. CSS and mako template are largely inspired by
c2c financial reports.
""",
    "data": [
        "hr_utilization_data.xml",
        "hr_utilization_view.xml",
        "wizard/hr_utilization_print.xml",
        "report/hr_utilization_report.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    'installable': False,
    "auto_install": False,
    "application": False,
}
