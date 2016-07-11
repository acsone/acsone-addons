# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class HrHolidays(models.Model):

    _inherit = 'hr.holidays'

    is_revaluation = fields.Boolean()

    _sql_constraints = [
        ('date_check',
         "CHECK ( number_of_days_temp >= 0 OR is_revaluation = True)",
         "The number of days must be greater than 0."),
    ]
