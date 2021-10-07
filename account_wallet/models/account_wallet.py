# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountWallet(models.Model):
    _name = "account.wallet"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Wallet"
    _check_company_auto = True

    name = fields.Char(
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
    )
    wallet_type_id = fields.Many2one(
        "account.wallet.type", "Wallet Type", required=True, ondelete="restrict"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="wallet_type_id.company_id",
        store=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        readonly=True,
    )
    balance = fields.Monetary(
        compute="_compute_balance",
        currency_field="company_currency_id",
        store=True,
        tracking=10,
    )
    active = fields.Boolean(default=True)
    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="account_wallet_id",
        string="Journal Items",
    )
    # TODO: Check if this is necessary
    # create_date = fields.Date(
    #    default=fields.Date.today)

    _sql_constraints = [
        (
            "wallet_uniq",
            "EXCLUDE (partner_id WITH =, wallet_type_id WITH =, company_id WITH =) "
            "WHERE (active=True)",
            "You can have just one active wallet for same type and partner by company",
        )
    ]

    @api.constrains("partner_id")
    def _check_partner(self):
        """Check there is no move lines to be able to set a partner"""
        for wallet in self:
            if wallet.partner_id and wallet.account_move_line_ids:
                raise ValidationError(
                    _("Partner can not be defined on a" " cagnotte with journal items")
                )
        return True

    def _get_name(self):
        """
        Get a composed display name from different properties

        """
        self.ensure_one()
        name = "{type} - {name}"
        values = {
            "type": self.wallet_type_id.name,
            "name": self.name,
        }
        if self.partner_id.name:
            name += " - {partner}"
            values.update(
                {
                    "partner": self.partner_id.name,
                }
            )
        return name.format(**values)

    # TODO: Add name_search
    def name_get(self):
        """Add the type of wallet in the name"""
        res = []
        for wallet in self:
            name = wallet._get_name()
            res.append((wallet.id, name))
        return res

    @api.model
    def _get_compute_balance_fields(self):
        return ["account_move_line_ids.debit", "account_move_line_ids.credit"]

    @api.depends(lambda self: self._get_compute_balance_fields())
    def _compute_balance(self):
        for wallet in self:
            balance = 0
            for move_line in wallet.account_move_line_ids:
                balance += move_line.credit - move_line.debit
            wallet.balance = balance

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" not in vals or vals["name"] == _("New"):
                wallet_type = self.env["account.wallet.type"].browse(
                    vals["wallet_type_id"]
                )
                vals["name"] = wallet_type.sequence_id.next_by_id()
        return super().create(vals_list)
