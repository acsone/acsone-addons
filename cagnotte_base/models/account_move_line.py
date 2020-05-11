# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_cagnotte_id = fields.Many2one(
        comodel_name='account.cagnotte',
        string='Cagnotte',
        ondelete='restrict')

    @api.model
    def cagnotte_value(self, values):
        """ If used account is on a cagnotte type,
            create a cagnotte
        """
        if not values.get('account_cagnotte_id'):
            comp = float_compare(values.get('credit', 0.0),
                                 0.0, precision_digits=2)
            if values.get('account_id') and comp != 0:
                cagnotte_type = self.env['cagnotte.type'].search(
                    [('account_id', '=', values['account_id'])])
                if cagnotte_type:
                    # create cagnotte
                    values['account_cagnotte_id'] = \
                        self.env['account.cagnotte'].create(
                            {'cagnotte_type_id': cagnotte_type.id}).id
        return values

    @api.model
    def create(self, values):
        vals = self.cagnotte_value(values)
        return super(AccountMoveLine, self).create(vals)

    @api.constrains('account_cagnotte_id', 'account_id')
    def _check_cagnotte_account(self):
        """ Account must correspond to cagnotte account
        """
        if any(l.account_cagnotte_id and
               l.account_cagnotte_id.cagnotte_type_id.account_id !=
               l.account_id for l in self):
            raise ValidationError(_("The account doesn't correspond"
                                    " to the cagnotte account"))
        return True
