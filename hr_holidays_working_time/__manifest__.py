# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "HR holidays working time",

    'summary': """
        Compute duration of leaves from the employee's working time""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Human resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'hr_holidays',
        'hr_employee_current_contract',
    ],
    'data': [
        'views/hr_holidays_view.xml',
    ],
}
