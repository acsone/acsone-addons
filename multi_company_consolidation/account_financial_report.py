# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of multi_company_consolidation, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     multi_company_consolidation is free software: you can redistribute it
#    and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     multi_company_consolidation is distributed in the hope that it will be
#     useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with multi_company_consolidation.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# No flake8 check to easy comparison with upstream
# flake8: noqa

from openerp.osv import fields, osv


class account_financial_report(osv.Model):
    _inherit = 'account.financial.report'

    def _get_balance(self, cr, uid, ids, field_names, args, context=None):
        """ Re-implementation of _get_balance for performance by pre-fetching the accounts.

        This method behaves like the original except it restricts the query to the
        chart_account_id that is present in the context if any. This is correct, as mixing accounts
        from different account charts does not make sense: when necessary this is done through
        consolidation children, which works with this method.
        """
        account_obj = self.pool.get('account.account')
        accounts_memoizer = context.get('accounts_memoizer')
        if accounts_memoizer is None:
            chart_account_id = context.get('chart_account_id')
            if chart_account_id:
                account_domain = [('id', 'child_of', chart_account_id)]
            else:
                account_domain = []
            account_ids = account_obj.search(cr, uid, account_domain, context=context)
            accounts_memoizer = dict((a['id'], a) for a in account_obj.read(cr, uid, account_ids, field_names, context=context))
            ctx2 = dict(context)
            ctx2['accounts_memoizer'] = accounts_memoizer
        else:
            ctx2 = context
        res = {}
        for report in self.read(cr, uid, ids, ['id', 'type', 'account_ids', 'account_type_ids', 'account_report_id', 'children_ids'], context=context):
            if report['id'] in res:
                continue
            res[report['id']] = dict((fn, 0.0) for fn in field_names)
            if report['type'] == 'accounts':
                # it's the sum of the linked accounts
                for account_id in report['account_ids']:
                    if account_id in accounts_memoizer:
                        for field in field_names:
                            res[report['id']][field] += accounts_memoizer[account_id][field]
            elif report['type'] == 'account_type' and report['account_type_ids']:
                # it's the sum the leaf accounts with such an account type
                account_ids = account_obj.search(cr, uid, [('user_type', 'in', report['account_type_ids']), ('type', '!=', 'view')], context=context)
                for account_id in account_ids:
                    if account_id in accounts_memoizer:
                        for field in field_names:
                            res[report['id']][field] += accounts_memoizer[account_id][field]
            elif report['type'] == 'account_report' and report['account_report_id']:
                # it's the amount of the linked report
                res2 = self._get_balance(cr, uid, [report['account_report_id'][0]], field_names, False, context=ctx2)
                for value in res2.values():
                    for field in field_names:
                        res[report['id']][field] += value[field]
            elif report['type'] == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._get_balance(cr, uid, [rec for rec in report['children_ids']], field_names, False, context=ctx2)
                for value in res2.values():
                    for field in field_names:
                        res[report['id']][field] += value[field]
        return res

    _columns = {
        'balance': fields.function(_get_balance, 'Balance', multi='balance'),
        'debit': fields.function(_get_balance, 'Debit', multi='balance'),
        'credit': fields.function(_get_balance, 'Credit', multi='balance'),
    }
