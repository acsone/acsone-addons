# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Mignon Laurent
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

import openerp.http as http
from openerp.http import request


class HelpOnlineController(http.Controller):

    def _get_view_name(self, model, view_type, domain=None, context=None):
        name = 'help-%s' % model.replace('.', '-')
        return name

    @http.route('/help_online/build_url', type='json', auth='user')
    def build_url(self, model, view_type, domain=None, context=None):
        view_model = request.env['ir.ui.view']
        user_model = request.env['res.users']
        if not user_model.has_group('help_online.help_online_group_reader'):
            return {}
        name = self._get_view_name(model, view_type, domain, context)
        res = view_model.search([('name', '=', name),
                                 ('page', '=', True)])
        if len(res):
            url = '/page/%s' % name
            if view_type:
                url = url + '#' + view_type
            return {'url': url,
                    'exists': True}
        elif user_model.has_group('help_online.help_online_group_writer'):
            return {'url': 'website/add/%s' % name,
                    'exists': False}
        else:
            return {}
