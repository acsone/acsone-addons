# -*- coding: utf-8 -*-
#
#
# Authors: Stéphane Bidoul & Olivier Laurent
# Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#

from datetime import date, timedelta

from openerp.osv import osv, fields


class hr_utilization_print(osv.TransientModel):
    _name = "hr.utilization.print"

    _columns = {
        'configuration_id': fields.many2one('hr.utilization.configuration',
                                            'Configuration', required=True),
        'period_start': fields.date("Period start", required=True),
        'period_end': fields.date("Period end", required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = {}

        period_end = date(date.today().year, date.today().month, 1)
        if date.today().month > 1:
            period_end -= timedelta(days=1)
        period_start = date(period_end.year, 1, 1)

        res['period_start'] = period_start.strftime("%Y-%m-%d")
        res['period_end'] = period_end.strftime("%Y-%m-%d")

        # if configurations exist, propose the first one
        configuration_obj = self.pool.get("hr.utilization.configuration")
        ids = configuration_obj.search(cr, uid, [])
        if ids:
            res['configuration_id'] = ids[0]
        return res

    def print_report(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        data = self.read(
            cr, uid, ids, ["configuration_id",
                           "period_start",
                           "period_end"], context)[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'hr.utilization.report',
                'datas': data}
