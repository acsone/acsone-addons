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
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_get_value_from_placeholder(common.TransactionCase):

    def setUp(self):
        super(test_get_value_from_placeholder, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_get_value_from_placeholder_method(self):
        """
        ======================================
        test_get_value_from_placeholder_method
        ======================================
        Try to call the method `get_value_from_placeholder_method`
        with an exemple of placeholder and check it is well evaluated
        """
        id_partner = self.registry("res.partner").create(
            self.cr, ADMIN_USER_ID, {'name': 'name_value'})
        _logger.info("create the partner %d", id_partner)

        expr = "object.name"

        real_value = self.registry("mail.compose.message").\
            get_value_from_placeholder(
                self.cr, ADMIN_USER_ID, id_partner, "res.partner", expr)
        self.assertEqual(real_value == "name_value", True, "The evaluated\
            expression have to match with the name of partner")
