# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_employee_current_contract,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_employee_current_contract is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_employee_current_contract is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_employee_current_contract.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    current_contract_id = fields.Many2one(
        comodel_name='hr.contract', string='Current contract',
        compute='_compute_current_contract')

    def _get_current_contract(self, date):
        self = self.sudo()
        contract_id = self.contract_ids.filtered(
            lambda r: r.date_start <= date and
            (not r.date_end or r.date_end >= date))
        if len(contract_id) > 1:
            contract_id = contract_id[0]
        return contract_id.id

    @api.one
    def _compute_current_contract(self):
        if not self.env.context.get('current_contract_date'):
            date = fields.Date.today()
        else:
            date = self.env.context.get('current_contract_date')
        contract_id = self._get_current_contract(date)
        self.current_contract_id = contract_id
