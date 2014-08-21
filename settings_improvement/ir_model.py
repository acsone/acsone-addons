# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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


class ir_model_data(orm.Model):

    _inherit = 'ir.model.data'

# private methods

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
