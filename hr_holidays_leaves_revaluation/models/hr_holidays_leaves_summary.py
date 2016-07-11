# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp import tools


class HrHolidaysLeavesSummary(models.Model):

    _name = 'hr.holidays.leaves.summary'
    _description = "Hr Holidays Leaves Summary"
    _auto = False

    employee_id = fields.Many2one(
         comodel_name='hr.employee', string='Employee')
    nb_remaining_days = fields.Integer()
    holiday_status_id = fields.Many2one(
        comodel_name='hr.holidays.status', string='Leaves Type')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_holidays_leaves_summary')
        cr.execute("""
        create or replace view hr_holidays_leaves_summary as (
            SELECT
                concat(employee_id,holiday_status_id) as id,
                employee_id,
                holiday_status_id,
                sum(number_of_days) as nb_remaining_days
            FROM hr_holidays
            WHERE
                (type = 'add' AND
                state = 'validate')
                or
                (type = 'remove' AND
                state not in ('refuse', 'cancel'))
            GROUP BY employee_id,holiday_status_id
        )""")
