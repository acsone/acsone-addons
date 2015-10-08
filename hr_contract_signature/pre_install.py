# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def logged_query(cr, query, args=None):
    if args is None:
        args = ()
    args = tuple(args) if type(args) == list else args
    cr.execute(query, args)
    _logger.debug('Running %s', query % args)
    _logger.debug('%s rows affected', cr.rowcount)
    return cr.rowcount


def rename_module(cr):
    old_names = ['acsone_hr_contract']
    new_name = 'hr_contract_signature'
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module in %s ")
    logged_query(cr, query, (new_name, tuple(old_names)))
    query = ("UPDATE ir_module_module_dependency SET name = %s "
             "WHERE name in %s")
    logged_query(cr, query, (new_name, tuple(old_names)))
