# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_analytic_project_id
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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


def set_account_analytic_account_project_id(cr, pool):
    '''
        Initialize the project_id field in case the module is
        installed when projects already exist
    '''
    cr.execute("""
            update account_analytic_account
                set project_id = (select id
                    from project_project where
                    analytic_account_id = account_analytic_account.id)
        """)
    return
