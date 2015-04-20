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

from openerp import fields, models
from openerp.tools.translate import _
from openerp.osv import osv


class account_fiscalyear(models.Model):
    _inherit = "account.fiscalyear"

    multi_company_consolidation = fields.Boolean(
        'Multi-company consolidation')


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    def _query_get(self, cr, uid, obj='l', context=None):
        """ When querying in multi-company consolidation mode, make sure we
        use periods as filter and not the fiscal year, since build_ctx_period
        restricts to one fiscal year (hence to one company) when a fiscal year
        is in the context.
        """
        fiscalyear_obj = self.pool['account.fiscalyear']
        fiscalyear_id = context.get('fiscalyear')
        fiscalyear = fiscalyear_id and fiscalyear_obj.browse(
            cr, uid, fiscalyear_id, context)
        multi_company_consolidation = (fiscalyear and
                                       fiscalyear.multi_company_consolidation)
        if multi_company_consolidation:
            # ensure we have a period filter and create a context without
            # fiscal year
            if not (context.get('periods') or (context.get('period_from') and
                                               context.get('period_to'))):
                raise osv.except_osv(
                    _('Error!'),
                    _("A period filter must be selected for multi-company "
                      "consolidation reports"))
            context = dict(context, fiscalyear=False, company_id=False)
        query = super(account_move_line, self)._query_get(
            cr, uid, obj, context)
        return query
