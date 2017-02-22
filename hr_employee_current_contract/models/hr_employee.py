# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    current_contract_id = fields.Many2one(
        comodel_name='hr.contract', string='Current contract',
        compute='_compute_current_contract')

    def _get_current_contract(self, date):
        self = self.sudo()
        contract_id = self.contract_ids.filtered(
            lambda r: r.date_start <= date and
            (not r.date_end or r.date_end >= date))
        if len(contract_id) > 1:
            contract_id = contract_id[0]
        return contract_id.id

    @api.one
    def _compute_current_contract(self):
        if not self.env.context.get('current_contract_date'):
            date = fields.Date.today()
        else:
            date = self.env.context.get('current_contract_date')
        contract_id = self._get_current_contract(date)
        self.current_contract_id = contract_id
