# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of project_code, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     project_code is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     project_code is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with project_code.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class project(orm.Model):
    _inherit = "project.project"

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, uid,
                              [('code', '=like', name + "%")] + args,
                              limit=limit)
            if not ids:
                ids = self.search(cr, uid,
                                  [('name', operator, name)] + args,
                                  limit=limit)
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - ' + name
            res.append((record['id'], name))
        return res


class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, uid, [('code', '=like', name + "%")] + args,
                              limit=limit)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args,
                                  limit=limit)
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        return self._get_full_name(cr, uid, ids, context=context)

    def _get_full_name(self, cr, uid, ids, name=None, args=None, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - ' + name
            res.append((record['id'], name))
        return res

    _columns = {
        'complete_name': fields.function(_get_full_name, type='char', string='Full Name'),
    }
