# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_contract_signature,
#     an Odoo module.
#
#     Authors: Stéphane Bidoul
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_contract_signature is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_contract_signature is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_contract_signature.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class hr_contract(models.Model):
    _inherit = "hr.contract"

    contract_signed = fields.Boolean(
        string='Contract Signed',
        help='Set this when the contract is signed by the contractor')
