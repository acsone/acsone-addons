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
VIEW_REPORT_DOCUMENT_ARCH = """
<t t-name="one2many_groups.report_dummy_document">
    <t t-call="report.html_container">
        <t t-foreach="doc_ids" t-as="doc_id">
            <t t-call="report.external_layout">
                <div class="page">
                    <div class="oe_structure"/>
                    <table class="table table-condensed" tree_grid_mode="1">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Total</th>
                            </tr>
                       </thead>
                       <tbody class="tbody" tree_grid_mode="1">
                            <tr t-foreach="o.member_model_ids" t-as="l">
                                <td>
                                   <span t-field="l.name"/>
                                </td>
                                <td>
                                   <span t-field="l.total"/>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="oe_structure"/>
                </div>
            </t>
        </t>
    </t>
</t>
"""
VIEW_REPORT_ARCH = """
<t t-name="one2many_groups.report_dummy">
    <t t-call="report.html_container">
        <t t-foreach="doc_ids" t-as="doc_id">
            <t t-raw="translate_doc(doc_id, doc_model, 'partner_id.lang',
            'one2many_groups.report_dummy_document')"/>
        </t>
    </t>
</t>
"""
