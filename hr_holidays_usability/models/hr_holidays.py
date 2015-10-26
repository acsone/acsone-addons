# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_usability,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_usability is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_usability is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_usability.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class hr_holidays(models.Model):
    _inherit = "hr.holidays"

    def _get_number_of_days(self, date_from, date_to):
        """ return -1, overriding the default behaviour (which computes
        a bogus value including week-ends, etc), this will
        force the user to enter a correct value, since 0 is not allowed
        """
        return -1

    number_of_days_temp = fields.Float(required=True)

    _sql_constraints = [
        # This is because hr_holidays says number_of_days_temp >= 0,
        # which IMO is a bug
        ('date_check3', "CHECK ( number_of_days_temp > 0 )",
         "The number of days must be greater than 0.")
    ]
