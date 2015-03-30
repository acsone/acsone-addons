# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of analytic_code, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     analytic_code is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     analytic_code is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with analytic_code.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    complete_name = fields.Char(compute='_get_full_name')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', '=like', name + "%")] + args,
                               limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)] + args,
                                   limit=limit)
        else:
            recs = self.search(args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        return self._get_full_name()

    @api.one
    @api.depends('name', 'code')
    def _get_full_name(self):
        self.complete_name = self.name
        if self.code:
            self.complete_name = self.code + ' - ' + self.name
