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

from openerp.addons.account.report import account_financial_report
from openerp.report import report_sxw
from openerp.osv import osv



class report_account_common(account_financial_report.report_account_common):
    """ Override the official account_financial_report algorithm for performance
    - pre-fetch accounts and limit account details to the selected account chart 
    - XXX possible improvement: pre-fetch comparison column

    Plus: prefix consolidation children accounts with the account plan name
    """

    def get_lines(self, data):
        def get_account_plan_name(account):
            if not account.parent_id:
                return account.name
            else:
                return get_account_plan_name(account.parent_id)

        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        data['form']['used_context']['state'] = data['form']['target_move']
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])
        new_context = dict(data['form']['used_context'], lang=self.context.get('lang', 'en_US'))
        direct_children = set(account_obj.search(self.cr, self.uid, [('id', 'child_of', new_context['chart_account_id'])], context=new_context))
        all_account_ids = account_obj._get_children_and_consol(self.cr, self.uid, new_context['chart_account_id'], context=new_context)
        all_accounts = account_obj.browse(self.cr, self.uid, all_account_ids, context=new_context)
        all_accounts_by_id = dict([(a.id, a) for a in all_accounts])
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=new_context):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form']['comparison_context']).balance * report.sign
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                parent_account_ids = [x.id for x in report.account_ids if x.id in direct_children]
                if parent_account_ids:
                    account_ids = account_obj._get_children_and_consol(self.cr, self.uid, parent_account_ids)
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
                account_ids = [account_id for account_id in account_ids if account_id in direct_children]
            if account_ids:
                for account_id in account_ids:
                    account = all_accounts_by_id.get(account_id)
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    if not account.id in direct_children:
                        prefix = "%s: " % get_account_plan_name(account)
                    else:
                        prefix = ""
                    vals = {
                        'name': prefix + account.code + ' ' + account.name,
                        'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        'account_type': account.type,
                    }

                    if data['form']['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        flag = True
                    if data['form']['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['comparison_context']).balance * report.sign
                        if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines


class report_financial(osv.AbstractModel):
    _inherit = 'report.account.report_financial'
    _wrapped_report_class = report_account_common
