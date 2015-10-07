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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    current_contract_id = fields.Many2one(
        comodel_name='hr.contract', string='Current contract',
        compute='_compute_current_contract')

    @api.one
    def _compute_current_contract(self):
        self = self.sudo()
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        contract_id = self.contract_ids.filtered(
            lambda r: r.date_start <= today and
            (not r.date_end or r.date_end >= today))
        if len(contract_id) > 1:
            contract_id = contract_id[0]
        self.current_contract_id = contract_id
