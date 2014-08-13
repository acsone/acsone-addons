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
from openerp.tools import SUPERUSER_ID

_MASS_MAILING_MODELS = []


class distribution_list(orm.Model):

    _inherit = 'distribution.list'

    def _register_hook(self, cr):
        """
        Call `_get_mailing_model` of `mail.mass_mailing` to set a `domain` on
        `dst_model_id` to keep consistency between resulting ids
        """
        super(distribution_list, self)._register_hook(cr)

        res = self.pool['mail.mass_mailing']._get_mailing_model(
            cr, SUPERUSER_ID)
        mass_mailing_models = []
        for model in res:
            mass_mailing_models.append(model[0])
        type(self).dst_model_id.domain = [('model', 'in', mass_mailing_models)]
