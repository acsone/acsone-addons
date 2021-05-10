# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.addons.cagnotte_base.tests.test_cagnotte import load_file


class TestCagnotte(common.TransactionCase):

    def setUp(self):
        super(TestCagnotte, self).setUp()
        load_file(
            self.cr,
            'cagnotte_base',
            'tests/data/',
            'account_cagnotte_data.xml')

    def test_cagnotte(self):
        """ Create cagnotte
            Check coupon code is empty
            Configure cagnotte type to generate coupon code
            Create cagnotte
            Check coupon code is filled
        """
        cagnotte_type = self.env.ref("cagnotte_base.cagnotte_type")
        cagnotte_obj = self.env['account.cagnotte']
        cagnotte = cagnotte_obj.create({'cagnotte_type_id': cagnotte_type.id})
        self.assertFalse(cagnotte.coupon_code)
        cagnotte_type.with_coupon_code = True
        cagnotte = cagnotte_obj.create({'cagnotte_type_id': cagnotte_type.id})
        self.assertTrue(cagnotte.coupon_code)
