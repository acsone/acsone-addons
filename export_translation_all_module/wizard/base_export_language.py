# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import api, fields, models


class BaseLanguageExport(models.TransientModel):
    _inherit = "base.language.export"

    @api.onchange('select_all_installed_module')
    def onchange_select_all_installed_module(self):
        for wiz in self:
            if not wiz.select_all_installed_module:
                wiz.modules = False
            else:
                domain = [('state', '=', 'installed')]
                wiz.modules = self.env['ir.module.module'].search(domain).ids

    select_all_installed_module = fields.Boolean()
