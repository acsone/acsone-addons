# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

PERIOD_SELECTION = [('morning', 'Morning'),
                    ('afternoon', 'Afternoon')]


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    periodofday = fields.Selection(
        string='Period Of Day',
        selection=PERIOD_SELECTION,
        default='morning',
        required=True
    )
