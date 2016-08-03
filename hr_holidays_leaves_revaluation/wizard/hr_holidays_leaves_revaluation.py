# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class HrHolidaysLeavesRevaluation(models.TransientModel):
    _name = 'hr.holidays.leaves.revaluation'
    _description = 'Hr Holidays Leaves Revaluation'

    @api.model
    def _get_revaluate_vals(self, employee_id, nb_hours):
        print nb_hours
        return {
            'name': 'Revaluation',
            'employee_id': employee_id,
            'holiday_status_id': self.holiday_status_id.id,
            'number_of_hours_temp': nb_hours,
            'type': 'add',
            'is_revaluation': True,
        }

    check_point_date = fields.Date(required=True)
    max_nb_hours_allowed = fields.Float(
        string='Maximum Number of hours allowed', required=True)
    holiday_status_id = fields.Many2one(
        comodel_name='hr.holidays.status', string='Leave Type', required=True)

    @api.multi
    def _get_sql_command(self):
        self.ensure_one()
        return """
        SELECT
            employee_id,
            create_date as create_date,
            holiday_status_id,
            sum(number_of_hours) as nb_remaining_hours
        FROM hr_holidays
        WHERE
            ((type = 'add' AND
            state = 'validate')
            or
            (type = 'remove' AND
            state not in ('refuse', 'cancel')))
            AND
            date_from <= '%s'
            AND holiday_status_id = %s
        GROUP BY employee_id,holiday_status_id,create_date;
        """ % (
            self.check_point_date, self.holiday_status_id.id)

    @api.multi
    def button_leaves_revaluation(self):
        self.ensure_one()
        hr_holidays_model = self.env['hr.holidays']
        self.env.cr.execute(self._get_sql_command())
        for v in self.env.cr.dictfetchall():
            if v['nb_remaining_hours'] > self.max_nb_hours_allowed:
                nb_hours_temp =\
                    self.max_nb_hours_allowed - v['nb_remaining_hours']
                hr_holidays_model.create(self._get_revaluate_vals(
                    v['employee_id'], nb_hours_temp))
