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
from lxml import etree
from openerp import models, api, fields


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        html_render = super(Report, self).get_html(
            cr, uid, ids, report_name, data=data, context=context)
        report = self._get_report_from_name(cr, uid, report_name)
        if report.tree_grid_model and ids:
            html_render = self.render_group(
                cr, uid, [report.id], report.tree_grid_model, html_render,
                ids[0], context=context)
        return html_render

    @api.multi
    def render_group(self, group, html_render, model_id):
        """
        """
        self.ensure_one()
        domain = [
            ('master_id', '=', model_id),
        ]
        if not self.env.registry.get(group):
            return html_render

        group_model = self.env[group]
        group_ids = group_model.search(domain)
        html = html_render
        if group_ids:
            html = etree.HTML(html_render)
            table_root = html.find('.//table[@tree_grid_mode="1"]')
            tbody = table_root.find('.//tbody')
            self.unify_header(table_root.find('.//thead//tr'))
            index_key = self.get_index_key(tbody)
            for group in group_ids:
                group_row = etree.fromstring(
                    group.get_html(index_key['nb_column']))
                if not group.parent_id:
                    tbody.insert(0, group_row)
                else:
                    group_last_brother = tbody.findall(
                        './/tr[@data-oe-parent_group_id="%s"]'
                        % group.parent_id.id)
                    if len(group_last_brother):
                        tbody.insert(
                            tbody.getchildren().index(
                                group_last_brother[-1])+1, group_row)
                    else:
                        group_parent = tbody.findall(
                            './/tr[@data-oe-group_id="%s"]'
                            % group.parent_id.id)
                        tbody.insert(
                            tbody.getchildren().index(group_parent[-1])+1,
                            group_row)
                group.add_complementary_fields(group_row, index_key)
	        idx = 0
                for member in group.members_ids:
                    last_element = tbody.find(
                        './/tr[@data-oe-group_id="%s"]' % group.id)
                    xpath_member_row = etree.XPath(
                        '//tr[td[descendant::span[@data-oe-id="%s"]]]'
                        % member.id)
                    member_row = xpath_member_row(tbody)
                    if len(member_row):
                        member_row = member_row[0]
                        member_row.attrib['data-oe-group_id'] = str(group.id)
                        member_row.attrib['data-oe-parent_group_id'] =\
                            str(group.parent_id.id)
                        self.unify_member(member_row)
                        idx += 1
                        tbody.insert(
                            tbody.getchildren().index(last_element) + idx,
                            member_row)
            return etree.tostring(html)
        else:
            return html

    @api.model
    def unify_header(self, tr):
        tr.insert(0, etree.fromstring(('<th></th>')))

    @api.model
    def unify_member(self, tr):
        tr.insert(0, etree.fromstring('<td></td>'))

    @api.model
    def get_index_key(self, tbody):
        xpath_tr = etree.XPath('.//tr[td[descendant::span[@data-oe-id]]]')
        tr = xpath_tr(tbody)
        res = {}
        if len(tr):
            all_td = tr[0].findall('.//td')
            res['nb_column'] = len(all_td)
            for idx, td in enumerate(all_td):
                attr_key = 'data-oe-field'
                [res.setdefault(span.attrib[attr_key], idx+1) for span in
                    td.findall('.//span') if attr_key in span.attrib]
        return res


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report.xml'

    tree_grid_model = fields.Char(String='Tree Grid Model')
