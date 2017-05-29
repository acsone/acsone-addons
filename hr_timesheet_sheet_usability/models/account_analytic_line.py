# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.onchange('date')
    def _onchange_date_in_details(self):
        """ Coerce date within timesheet period """
        date_from = self.sheet_id.date_from
        date_to = self.sheet_id.date_to
        if self.date and date_from and date_to:
            if self.date < date_from:
                self.date = date_from
            if self.date > date_to:
                self.date = date_to
