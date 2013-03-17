# -*- encoding: utf-8 -*-
##############################################################################
#
# Author: Stéphane Bidoul
# Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
# All Right Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'Belgium - Multilingual Chart of Accounts (en/nl/fr) - Acsone Extension',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "ACSONE SA/NV",
    'maintainer': "ACSONE SA/NV",
    'website': "http://acsone.eu/",
    'category' : 'Localization/Account Charts',
    'description': """
    
    Belgian localisation (on top of l10n_be) - Extension:
    * add account groups 166, 167 and 169 to Balance Sheet "Other Liabilities and Charges (163/5)"
    * add line to Balance Sheet: "Unallocated Unallocated Profits (Losses) of Current Fiscal Year" to equilibrate the balance sheet when the fiscal year is not yet closed (add accounts 6 & 7 to it manually)
        
    """,
    'depends': ['l10n_be_coa_multilang'],
    'demo_xml': [],
    'init_xml': [],
    'update_xml' : [
        'account_financial_report.xml',        
        'be_legal_financial_reportscheme.xml',        
    ],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
