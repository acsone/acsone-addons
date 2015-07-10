# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of one2many_groups,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     one2many_groups is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     one2many_groups is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with one2many_groups.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        html_render = super(Report, self).get_html(
            cr, uid, ids, report_name, data=data, context=context)
        report = self._get_report_from_name(cr, uid, report_name)
        if report.tree_grid_model:
            html_render = self.render_group(
                cr, uid, [report.id], html_render, model_ids=ids, context=None)
        return html_render

    @api.multi
    def render_group(self, html_render, model_ids):
        self.ensure_one()
        return html_render


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report.xml'

    tree_grid_model = fields.Char(String='Tree Grid Model')
