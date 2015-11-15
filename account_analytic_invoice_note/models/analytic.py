# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_analytic_invoice_note,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_analytic_invoice_note is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_analytic_invoice_note is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_analytic_invoice_note.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class analytic_account(models.Model):
    _inherit = "account.analytic.account"

    invoice_note = fields.Text(
        'Invoice note',
        help="This note will appear on invoices; typically "
             "the purchase order number or customer reference")


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def invoice_cost_create(self, data={}):
        invoice_ids = super(account_analytic_line, self)\
            .invoice_cost_create(data)
        invoice_obj = self.env['account.invoice']
        for invoice in invoice_obj.browse(invoice_ids):
            aa_ids = set()
            for line in invoice.invoice_line:
                aa_ids.add(line.account_analytic_id.id)
            if len(aa_ids) == 1:
                # all lines share the same analytic account
                # (this is how the default works, but better be safe)
                account = invoice.invoice_line[0].account_analytic_id
                invoice.write({
                    'reference': account.complete_name,
                    'name': " ".join((account.invoice_note or "").split("\n")),
                })
        return invoice_ids
