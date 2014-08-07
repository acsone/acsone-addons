# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.tools.safe_eval import safe_eval as eval


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def get_value_from_placeholder(self, cr, uid, id_record, model, expr,
                                   context=None):
        """
        :type id_record: integer
        :param id_record: id of the concerned record
        :type model: string
        :param model: name of the concerned model
        :type expr: string
        :param expr: expression to evaluated
        :rtype: string
        :rparam: evaluated expression

        **Note**
        If `expr` make an exception then return empty string
        """
        record = self.pool.get(model).browse(
            cr, uid, id_record, context=context)
        try:
            value = eval(expr, {'object': record})
        except:
            value = ""
        return value
