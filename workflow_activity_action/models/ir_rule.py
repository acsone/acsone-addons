# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.cr_uid
    def clear_cache(self, cr, uid):
        res = super(IrRule, self).clear_cache(cr, uid)
        self.pool['activity.record.rule'].clear_cache(cr, uid)
        return res
