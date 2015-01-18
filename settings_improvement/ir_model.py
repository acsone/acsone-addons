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


class ir_model(orm.Model):
    _inherit = 'ir.model'

    def _drop_table(self, cr, uid, ids, context=None):
        '''
        Continue unlink process when obsolete model is no more registered
        Note: therefore PG object could not be destroyed
        '''
        try:
            super(ir_model, self)._drop_table(
                self, cr, uid, ids, context=context)
        except:
            pass

        return True
