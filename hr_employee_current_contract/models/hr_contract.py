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

from openerp import models, fields, api, exceptions, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # I remove the required attribute on the field to allow to do a duplicate
    date_start = fields.Date(required=False, copy=False, default=False)
    date_end = fields.Date(copy=False)

    @api.one
    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_contract_overlap(self):
        if self.date_start:
            if self.date_end:
                where = "(date_start <= %s and ((date_end is null) or \
                    (%s <= date_end)))"
                where_params = [self.date_end, self.date_start]
            else:
                where = "((date_end is null) or (%s <= date_end))"
                where_params = [self.date_start]
            where = '(' + where + ' and id <> %s and employee_id = %s)'
            where_params += [self.id, self.employee_id.id]
            self._cr.execute('SELECT id \
                        FROM hr_contract \
                        WHERE ' + where + '', tuple(where_params))
            if self._cr.fetchall():
                raise exceptions.Warning(
                    _('You cannot have 2 contracts that overlap!'))
