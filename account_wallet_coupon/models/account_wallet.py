# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountWallet(models.Model):
    _inherit = "account.wallet"

    coupon_id = fields.Many2one(
        comodel_name="coupon.coupon",
        copy=False,
    )

    def _get_name(self):
        self.ensure_one()
        name = super()._get_name()
        return "{name} - {coupon}".format(
            name=name, coupon=self.coupon_id.code)

    _sql_constraints = [(
        'coupon_cagnotte_uniq',
        'unique(coupon_id, wallet_type_id)',
        'A wallet with same type and coupon already exists'
    )]

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not vals.get('coupon_id') and vals.get('wallet_type_id'):
            wallet_type = self.env['account.wallet.type'].browse(
                vals['wallet_type_id'])
            if wallet_type.with_coupon_code:
                res.sudo().coupon_id = self.env["coupon.coupon"].create({})
        return res
