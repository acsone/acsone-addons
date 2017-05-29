# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "HR employee contract job",
    'summary': """
        Provide employee's job directly from the current contract""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract',
        'hr_employee_current_contract',
    ],
    'data': [
        'views/hr_employee_view.xml',
    ],
}
