# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CagnotteType(models.Model):
    _inherit = 'cagnotte.type'

    check_cagnotte_amount = fields.Boolean()
