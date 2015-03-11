# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Acsone SA/NV
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

from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class account_account(orm.Model):

    _inherit = 'account.account'

    def _check_coa_loaded(self, cr, uid, company_id, tmpl_id, context=None):
        """
        Intended to be override to determine if a COA is already loaded
        for a specific company
        """
        account_id = self.search(
            cr, uid,
            [('company_id', '=', company_id)],
            limit=1, context=context)
        return account_id


class wizard_multi_charts_accounts(orm.TransientModel):
    """
    Execute wizard automatically without showing the wizard popup window
    """
    _inherit = 'wizard.multi.charts.accounts'

    def auto_execute(self, cr, uid, ids=False, context=None):
        """
        Load a COA if not already loaded
        """
        context = dict(context or {})
        context['lang'] = 'en_US'
        if not ids:
            ids = self.search(cr, uid, [], context=context)
        account_obj = self.pool.get('account.account')
        for wz in self.browse(cr, uid, ids, context=context):
            loaded = account_obj._check_coa_loaded(
                cr, uid, wz.company_id.id, wz.chart_template_id.id,
                context=context)
            if not loaded:
                # execute original wizard method
                _logger.info('Configure Accounting Data for Company: %s' % (
                    wz.company_id.name,))
                self.execute(cr, uid, [wz.id], context=context)
