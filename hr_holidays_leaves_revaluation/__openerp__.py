# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "HR Holidays Leaves Revaluation",

    'summary': """
        This module adds menu entry that allows to launch a wizard to control
        the number of available holidays per type and per employee. It also
        allows to decrease this number depending of a maximum allowed days""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'HR',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_holidays_leaves_revaluation_wizard_view.xml',
    ],
}
