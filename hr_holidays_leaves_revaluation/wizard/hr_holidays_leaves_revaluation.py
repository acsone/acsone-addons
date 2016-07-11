# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class HrHolidaysLeavesRevaluation(models.TransientModel):
    _name = 'hr.holidays.leaves.revaluation'
    _description = 'Hr Holidays Leaves Revaluation'

    @api.model
    def _get_revaluate_vals(self, employee_id, nb_days):
        return {
            'name': 'Revaluation',
            'employee_id': employee_id,
            'holiday_status_id': self.holiday_status_id.id,
            'number_of_days_temp': nb_days,
            'type': 'add',
            'is_revaluation': True,
        }

    max_nb_days_allowed = fields.Integer(
        string='Maximum Number of days allowed', required=True)
    holiday_status_id = fields.Many2one(
        comodel_name='hr.holidays.status', string='Leave Type', required=True)

    @api.multi
    def button_leaves_revaluation(self):
        self.ensure_one()
        hr_holidays_leaves_summary_model =\
            self.env['hr.holidays.leaves.summary']
        hr_holidays_model = self.env['hr.holidays']
        domain = [
            ('nb_remaining_days', '>', self.max_nb_days_allowed),
            ('holiday_status_id', '=', self.holiday_status_id.id)
        ]
        leaves_revaluation_ids =\
            hr_holidays_leaves_summary_model.search(domain)
        for leaves_revaluation_id in leaves_revaluation_ids:
            nb_days = self.max_nb_days_allowed -\
                leaves_revaluation_id.nb_remaining_days
            hr_holidays_model.create(self._get_revaluate_vals(
                leaves_revaluation_id.employee_id.id, nb_days))
