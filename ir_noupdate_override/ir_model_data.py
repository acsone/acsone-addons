# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of ir_noupdate_override, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     ir_noupdate_override is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     ir_noupdate_override is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with ir_noupdate_override.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models


class ir_model_data(models.Model):

    _inherit = 'ir.model.data'

    def _update(self, cr, uid, model, module, values,
                xml_id=False, store=True, noupdate=False,
                mode='init', res_id=False,
                context=None):
        '''
        Let's the developer to decide if a record is updatable or not
        I.e force the init mode if the data tag is marked noupdate="0"
        '''
        if not noupdate and mode == 'update':
            mode = 'init'
        res = super(ir_model_data, self)._update(
            cr, uid, model, module, values,
            xml_id=xml_id, store=store, noupdate=noupdate,
            mode=mode, res_id=res_id,
            context=context)
        return res
