# -*- coding: utf-8 -*-
#
#
#    Authors: Adrien Peiffer
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
#

from openerp.osv import fields, orm
from openerp import SUPERUSER_ID


_parameters = {
    "companyweb.login": "",
    "companyweb.pswd": "",
}


class account_companyweb_config_settings(orm.TransientModel):
    _name = 'account.companyweb.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'companyweb_login': fields.char('Login', 16),
        'companyweb_pswd': fields.char('Password', 16),
    }

    def init(self, cr, force=False):
        config_parameter_model = self.pool.get('ir.config_parameter')
        for key, value in _parameters.iteritems():
            ids = not force and config_parameter_model.search(
                cr, SUPERUSER_ID, [('key', '=', key)])
            if not ids:
                config_parameter_model.set_param(cr, SUPERUSER_ID, key, value)

    def get_default_companyweb_login(self, cr, uid, fields, context=None):
        login = self.pool.get('ir.config_parameter').get_param(
            cr, SUPERUSER_ID, 'companyweb.login', False)
        return {'companyweb_login': login}

    def get_default_companyweb_pswd(self, cr, uid, fields, context=None):
        pswd = self.pool.get('ir.config_parameter').get_param(
            cr, SUPERUSER_ID, 'companyweb.pswd', False)
        return {'companyweb_pswd': pswd}

    def set_default_companyweb_login(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        self.pool.get('ir.config_parameter').set_param(
            cr, SUPERUSER_ID, 'companyweb.login', config.companyweb_login)
        return True

    def set_default_companyweb_pswd(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        self.pool.get('ir.config_parameter').set_param(
            cr, SUPERUSER_ID, 'companyweb.pswd', config.companyweb_pswd)
        return True
