# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountCagnotte(models.Model):

    _inherit = "account.cagnotte"

    no_negative = fields.Boolean(
        track_visibility="onchange",
        default=lambda self: self.cagnotte_type_id.no_negative,
    )
    is_negative = fields.Boolean(
        compute="_compute_is_negative",
        store=True,
    )

    @api.multi
    @api.onchange("cagnotte_type_id")
    def _onchange_cagnotte_type_id(self):
        for cagnotte in self:
            if not cagnotte.no_negative:
                cagnotte.no_negative = cagnotte.cagnotte_type_id.no_negative

    @api.multi
    @api.constrains("solde_cagnotte", "no_negative")
    def _check_no_negative(self):
        for cagnotte in self.filtered("no_negative"):
            if cagnotte.solde_cagnotte < 0:
                raise ValidationError(
                    _("The cagnotte balance cannot be negative !"))

    @api.multi
    @api.depends("solde_cagnotte")
    def _compute_is_negative(self):
        negative_cagnottes = self.filtered(lambda c: c.solde_cagnotte < 0)
        negative_cagnottes.update({"is_negative": True})

    @api.model
    def _update_vals_no_negative(self, vals):
        if "cagnotte_type_id" in vals and "no_negative" not in vals:
            cagnotte_type = self.env["cagnotte.type"].browse(
                vals["cagnotte_type_id"])
            vals.update({"no_negative": cagnotte_type.no_negative})
        return vals

    @api.model
    def create(self, vals):
        self._update_vals_no_negative(vals)
        return super(AccountCagnotte, self).create(vals)
