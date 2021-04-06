# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CagnotteType(models.Model):

    _inherit = "cagnotte.type"

    no_negative = fields.Boolean(
        help="Check this if you want new cagnotte with this type constrained"
        "to not allow negative balance."
    )
