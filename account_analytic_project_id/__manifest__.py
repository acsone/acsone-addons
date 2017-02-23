# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Stéphane Bidoul
#    Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
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
##############################################################################

{
    "name": "Account Analytic Project Id",
    'summary': "This module adds a project_id field on analytic account.",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "category": "Accounting & Finance",
    "depends": ["analytic", "project"],
    "license": "AGPL-3",
    'installable': False,
    "auto_install": False,
    "application": False,
    'post_init_hook': 'set_account_analytic_account_project_id',
}
