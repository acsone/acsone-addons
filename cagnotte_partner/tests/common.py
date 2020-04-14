# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.cagnotte_base.tests.common import CagnotteCommon


class CagnotteCommonPartner(CagnotteCommon):

    @classmethod
    def setUpClass(cls):
        super(CagnotteCommonPartner, cls).setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.cagnotte.partner_id = cls.partner
