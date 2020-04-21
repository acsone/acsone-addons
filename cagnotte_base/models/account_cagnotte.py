# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountCagnotte(models.Model):
    _name = 'account.cagnotte'

    name = fields.Char(
        readonly=True,
        copy=False)
    cagnotte_type_id = fields.Many2one(
        'cagnotte.type',
        'Cagnotte Type',
        required=True,
        ondelete='restrict')
    company_currency_id = fields.Many2one(
        related='cagnotte_type_id.company_id.currency_id',
        readonly=True,
    )
    solde_cagnotte = fields.Monetary(
        compute='_compute_solde_cagnotte',
        currency_field='company_currency_id',
        store=True)
    active = fields.Boolean(
        default=True)
    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="account_cagnotte_id",
        string="Journal Items")
    create_date = fields.Date(
        default=fields.Date.today)
    solde_cagnotte_button = fields.Monetary(
        related="solde_cagnotte",
        readonly=True,
    )

    @api.multi
    def _get_name(self):
        self.ensure_one()
        return '%s - %s' % (self.cagnotte_type_id.name, self.name)

    @api.multi
    def name_get(self):
        """Add the type of cagnotte in the name"""
        res = []
        for cagnotte in self:
            name = cagnotte._get_name()
            res.append((cagnotte.id, name))
        return res

    @api.multi
    @api.depends('account_move_line_ids.debit',
                 'account_move_line_ids.credit')
    def _compute_solde_cagnotte(self):
        for cagnotte in self:
            solde_cagnotte = 0
            for move_line in cagnotte.account_move_line_ids:
                solde_cagnotte += move_line.credit - move_line.debit
            cagnotte.solde_cagnotte = solde_cagnotte

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            cagnotte_type = self.env['cagnotte.type'].browse(
                vals['cagnotte_type_id'])
            vals['name'] = cagnotte_type.sequence_id.next_by_id()
        return super(AccountCagnotte, self).create(vals)
