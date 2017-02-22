# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # I remove the required attribute on the field to allow to do a duplicate
    date_start = fields.Date(required=False, copy=False, default=False)
    date_end = fields.Date(copy=False)

    @api.one
    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_contract_overlap(self):
        if self.date_start:
            if self.date_end:
                where = "(date_start <= %s and ((date_end is null) or \
                    (%s <= date_end)))"
                where_params = [self.date_end, self.date_start]
            else:
                where = "((date_end is null) or (%s <= date_end))"
                where_params = [self.date_start]
            where = '(' + where + ' and id <> %s and employee_id = %s)'
            where_params += [self.id, self.employee_id.id]
            self._cr.execute('SELECT id \
                        FROM hr_contract \
                        WHERE ' + where + '', tuple(where_params))
            if self._cr.fetchall():
                raise exceptions.Warning(
                    _('You cannot have 2 contracts that overlap!'))
