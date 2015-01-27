# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Pigeon Cédric
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
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
from anybox.testing.openerp import SharedSetupTransactionCase


class test_pricelist(SharedSetupTransactionCase):
    _data_files = (
        'data/tests_data.xml',
    )

    _module_ns = 'tiered_pricing'

    def setUp(self):
        super(test_pricelist, self).setUp()
        self.env['ir.model'].clear_caches()
        self.registry['ir.model.data'].clear_caches()

        self.product_id = self.ref('%s.product_pricelist_test'
                                   % self._module_ns)
        pricelist_id = self.ref('%s.list0'
                                % self._module_ns)
        self.pricelist = self.env['product.pricelist'].browse(
            pricelist_id)

    def test_tiered_pricing(self):
        """
            Pricing:
                1   -  100 Pc : 0.29 €/Unit
                101 -  300 Pc : 0.26 €/Unit
                301 - 1000 Pc : 0.23 €/Unit
                + 1000 Pc     : 0.20 €/Unit
        """
        prices = (0.29, 0.26, 0.23, 0.20)
        splits = [(10, 0, 0, 0),
                  (100, 3, 0, 0),
                  (100, 200, 41, 0),
                  (100, 200, 700, 420)]
        for split in splits:
            qty = sum([x for x in split])
            expected_price = sum([split[idx] * prices[idx]
                                  for idx in range(len(split))])
            unit_price = self.pricelist.price_get(self.product_id, qty)
            amount = qty * unit_price[self.pricelist.id]
            self.assertAlmostEqual(amount, expected_price, 2)
