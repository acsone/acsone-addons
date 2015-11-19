# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_details_report,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_details_report is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_details_report is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_details_report.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models
import math


class FloatTimeConverter(models.AbstractModel):
    _name = 'ir.qweb.field.float_time'
    _inherit = 'ir.qweb.field'

    def value_to_html(self, cr, uid, value, field, options=None, context=None):
        hour = int(math.floor(value))
        minute = int(round((value % 1) * 60))
        return "%d:%02d" % (hour, minute)
