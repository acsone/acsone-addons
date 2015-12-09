# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountCagnotte(models.Model):
    _inherit = 'account.cagnotte'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")

    @api.one
    def name_get(self):
        """Add partner to the name"""
        res = super(AccountCagnotte, self).name_get()[0]
        if self.partner_id:
            res = (res[0], "%s, %s" % (res[1], self.partner_id.name))
        return res

    @api.multi
    def _check_partner(self):
        """ Check there is no move lines to be able to set a partner
        """
        for cagnotte in self:
            if cagnotte.partner_id and cagnotte.account_move_line_ids:
                return False
        return True

    _constraints = [
        (_check_partner,
         'Partner can not be defined on a cagnotte with journal items',
         ['partner_id']),
    ]

    _sql_constraints = [(
        'partner_cagnotte_uniq',
        'unique(partner_id, cagnotte_type_id)',
        'A cagnotte with cagnotte type and partner already exist'
    )]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def cagnotte_value(self, values):
        """ If cagnotte is set on move line, set partner to cagnotte partner
        """
        values = super(AccountMoveLine, self).cagnotte_value(values)
        if values.get('account_cagnotte_id'):
            cagnotte = self.env['account.cagnotte'].browse(
                values['account_cagnotte_id'])
            values['partner_id'] = cagnotte.partner_id.id
        return values
