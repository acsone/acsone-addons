# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "HR employee current contract",

    'summary': """
        Compute the current contract on employee""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_contract',
    ],
    'data': [
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
    ],
}
