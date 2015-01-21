# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Laurent Mignon
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

import logging
from openerp import http
from openerp.osv import orm
from openerp.http import request
from openerp.addons.web.controllers.main import DataSet

_logger = logging.getLogger(__name__)


class service_logger(orm.TransientModel):
    _name = "service.logger"
    _auto = False

    def log_fct(self, cr, uid, model, method, *args, **kw):
        """
        Logging function: This function is performing the logging operation
        @param model: Object whose values are being changed
        @param method: method to log: create, read, write, unlink, action or
         workflow action

        """
        _logger.info("%s %s.%s %s %s", uid, model, method, args or '',
                     kw or '')

    def log_fct_result(self, cr, uid, model, method, res, *args, **kw):
        """
        Logging function result: This function can be used to perform the
         logging operation of the function result
        @param model: Object whose values are being changed
        @param method: method to log: create, read, write, unlink, action or
         workflow action
        @param res: method return value
        """
        pass

    def log_fct_exception(self, cr, uid, model, method, ex, *args, **kw):
        """
        Logging function exception: This function can be used to perform the
         logging operation of an exception raised by the function
        @param model: Object whose values are being changed
        @param method: method to log: create, read, write, unlink, action or
         workflow action
        @param ex: exception raised
        """
        pass


class LoggerDataSet(DataSet):

    def _call_kw(self, model, method, args, kw):
        service_logger_obj = request.registry.get('service.logger')
        cr = request.cr
        uid = request.uid
        if service_logger_obj:
            service_logger_obj.log_fct(cr, uid, model, method, args, kw)
        try:
            res = super(LoggerDataSet, self)._call_kw(model, method, args, kw)
            if service_logger_obj:
                service_logger_obj.log_fct_result(
                    cr, uid, model, method, res, args, kw)
            return res
        except Exception, e:
            if service_logger_obj:
                service_logger_obj.log_fct_exception(
                    cr, uid, model, method, e, args, kw)
            raise

    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'],
                type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        return self._call_kw(model, method, args, kwargs)
