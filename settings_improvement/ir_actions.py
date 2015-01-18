# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of settings_improvements, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     settings_improvements is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     settings_improvements is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with settings_improvements.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class act_window(orm.Model):
    _inherit = 'ir.actions.act_window'

    def button_goto_action(self, cr, uid, act_id, context=None):
        if isinstance(act_id, (int, long)):
            act_id = [act_id]
        action = self.read(cr, uid, act_id, [], context)[0]
        action.update({'groups_id': False,
                       'search_view': False,
                       })
        return action
