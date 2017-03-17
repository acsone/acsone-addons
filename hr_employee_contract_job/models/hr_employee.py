# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    use_job_from_contract = fields.Boolean(
        string='Use contract job',
        help='Check this box to use the job from the current contract',
    )
    contract_job_id = fields.Many2one(
        string='Job Title',
        related='current_contract_id.job_id',
        readonly=True,
    )
