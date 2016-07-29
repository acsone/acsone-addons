# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp import fields
import datetime
from datetime import date


class TestHrHolidaysLeavesRevaluation(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysLeavesRevaluation, self).setUp()
        self.res_partner_mod = self.env['res.partner']
        self.res_users_mod = self.env['res.users']
        self.hr_employee_mod = self.env['hr.employee']
        self.hr_holidays_mod = self.env['hr.holidays']
        self.hr_holidays_satus_mod = self.env['hr.holidays.status']
        self.hr_holidays_leaves_revaluation_mod =\
            self.env['hr.holidays.leaves.revaluation']

    def test_hr_holidays_leaves_revaluation(self):
        vals = {
            'name': 'name',
            'email': 'name@email.com',
        }
        partner_id = self.res_partner_mod.create(vals)
        vals = {
            'partner_id': partner_id.id,
            'login': 'login',
        }
        user_id = self.res_users_mod.create(vals)
        vals = {
            'name': 'name',
            'user_id': user_id.id,
        }
        emp_id = self.hr_employee_mod.create(vals)
        holiday_status_id = self.hr_holidays_satus_mod.search([], limit=1)
        self.assertTrue(
            holiday_status_id, 'Should have at least one leave type')
        base = 42
        revaluated = 25
        vals = {
            'name': 'Legal leaves 2042',
            'employee_id': emp_id.id,
            'holiday_status_id': holiday_status_id.id,
            'number_of_hours_temp': base,
            'type': 'add',
        }
        allocation_id = self.hr_holidays_mod.create(vals)
        allocation_id.signal_workflow('validate')
        date_t = date.today() + datetime.timedelta(days=1)
        vals = {
            'check_point_date': fields.Date.to_string(date_t),
            'max_nb_hours_allowed': revaluated,
            'holiday_status_id': holiday_status_id.id,
        }
        wiz_id = self.hr_holidays_leaves_revaluation_mod.create(vals)
        wiz_id.button_leaves_revaluation()
        domain = [
            ('number_of_days_temp', '<', 0),
            ('type', '=', 'add'),
            ('holiday_status_id', '=', holiday_status_id.id),
        ]
        revaluate_holidays_id = self.hr_holidays_mod.search(domain, limit=1)
        self.assertTrue(revaluate_holidays_id, 'Should find one')
        self.assertEquals(
            revaluate_holidays_id.state, 'confirm',
            'should be in state confirm')
