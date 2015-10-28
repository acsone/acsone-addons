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

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
from openerp import exceptions


def create_simple_contract(self, employee, date_start, date_end=False):
    vals = {
        'name': 'Test',
        'employee_id': employee.id,
        'date_start': date_start,
        'date_end': date_end,
        'wage': 1.0,
    }
    return self.hr_contract_obj.create(vals)


class TestHrEmployeeCurrentContract(common.TransactionCase):

    def setUp(self):
        super(TestHrEmployeeCurrentContract, self).setUp()
        self.hr_contract_obj = self.env['hr.contract']
        self.employee01 = self.env.ref('hr.employee_vad')
        self.employee02 = self.env.ref('hr.employee_al')

    def test_contract_overlap(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterdaym1 = (datetime.now() - timedelta(days=2))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterdaym2 = (datetime.now() - timedelta(days=3))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        tommorow = (datetime.now() + timedelta(days=1))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        tommorowp1 = (datetime.now() + timedelta(days=2))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        tommorowp2 = (datetime.now() + timedelta(days=3))\
            .strftime(DEFAULT_SERVER_DATE_FORMAT)
        # Yesterday -> Tomorrow
        create_simple_contract(self, self.employee01, yesterday, tommorow)
        # Today -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                today, today)
        # Today -> Tommorow + 1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                today, tommorowp1)
        # Yesterday - 1 -> Tommorow +1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                yesterdaym1, tommorowp1)
        # Yesterday - 1 -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                yesterdaym1, today)
        # Yesterday -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                yesterday, today)
        # Today -> Tommorow
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                today, tommorow)
        # Tommorow -> Tommorow + 1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                tommorow, tommorowp1)
        # Yesterday -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                yesterday)
        # Today -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01, today)
        # Yesterday - 1 -> ..
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                yesterdaym1)
        # Tommorow -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee01,
                                                tommorow)
        contract02 = create_simple_contract(self, self.employee01, tommorowp1)
        contract02.unlink()
        contract02 = create_simple_contract(self, self.employee01, tommorowp1,
                                            tommorowp2)
        contract02.unlink()
        contract02 = create_simple_contract(self, self.employee01, yesterdaym2,
                                            yesterdaym1)
        contract02.unlink()
        # Yesterday -> ...
        create_simple_contract(self, self.employee02, yesterday)
        # Yesterday - 1 -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterdaym1, today)
        # Yesterday - 1 -> yesterday
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterdaym1, yesterday)
        # Today -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                today, today)
        # Today -> Tommorow + 1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                today, tommorowp1)
        # Yesterday - 1 -> Tommorow +1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterdaym1, tommorowp1)
        # Yesterday - 1 -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterdaym1, today)
        # Yesterday -> Today
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterday, today)
        # Today -> Tommorow
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                today, tommorow)
        # Tommorow -> Tommorow + 1
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                tommorow, tommorowp1)
        # Yesterday -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterday)
        # Today -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02, today)
        # Yesterday - 1 -> ..
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                yesterdaym1)
        # Tommorow -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                tommorow)
        # Tommorow + 1 -> ...
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                tommorowp1)
        # Tommorow + 1 -> Tommorow + 2
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            contract02 = create_simple_contract(self, self.employee02,
                                                tommorowp1, tommorowp2)
        contract02 = create_simple_contract(self, self.employee02, yesterdaym2,
                                            yesterdaym1)
        contract02.unlink()
