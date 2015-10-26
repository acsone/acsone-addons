# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_analytic_invoice_note,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_analytic_invoice_note is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_analytic_invoice_note is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_analytic_invoice_note.
#     If not, see <http://www.gnu.org/licenses/>.
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


def move_fields(cr):
    field_name = ['field_account_analytic_account_invoice_note']
    module_name = 'account_analytic_invoice_note'
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE name in %s ")
    logged_query(cr, query, (module_name, tuple(field_name)))
