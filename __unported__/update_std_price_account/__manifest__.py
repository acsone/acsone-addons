# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
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
##############################################################################

{
    "name": "Update standard price - account",
    "version": "0.1",
    "author": "ACSONE SA/NV",
    "category": "Other",
    "website": "http://www.acsone.eu",
    "depends": ["stock",
                ],
    "description": """
Update standard price - account
===============================

When updating the standard price (for products using the average
stock valuation method), allow the selection of the account to
use for stock valuation.

""",
    "data": ['stock_change_standard_price_view.xml'],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": False,
    "auto_install": False,
    "application": False,
}
