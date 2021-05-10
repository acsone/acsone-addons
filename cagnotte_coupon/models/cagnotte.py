# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid
from odoo import api, fields, models


class CagnotteType(models.Model):
    _inherit = 'cagnotte.type'

    with_coupon_code = fields.Boolean(
        help="Use this check to generate coupon number on created cagnotte "
             "for this type")


class AccountCagnotte(models.Model):
    _inherit = 'account.cagnotte'

    coupon_code = fields.Char(copy=False)

    @api.multi
    def _get_name(self):
        self.ensure_one()
        name = super(AccountCagnotte, self)._get_name()
        return '%s, %s' % (name, self.coupon_code)

    _sql_constraints = [(
        'coupon_cagnotte_uniq',
        'unique(coupon_code, cagnotte_type_id)',
        'A cagnotte with cagnotte type and coupon already exist'
    )]

    @api.model
    def generate_coupon_code(self, base):
        uid = hash(str(uuid.uuid1())) % 1000000
        return "%s%s" % (uid, base)

    @api.model
    def create(self, vals):
        res = super(AccountCagnotte, self).create(vals)
        if not vals.get('coupon_code') and vals.get('cagnotte_type_id'):
            cagnotte_type = self.env['cagnotte.type'].browse(
                vals['cagnotte_type_id'])
            if cagnotte_type.with_coupon_code:
                res.sudo().coupon_code = self.generate_coupon_code(res.id)
        return res
