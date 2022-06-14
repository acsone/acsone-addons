# © 2022  Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_move_credit_notes_wallet_default_product = fields.Many2one(
        comodel_name="product.product",
        string="Default product for credit note with wallet",
        config_parameter="account_move_credit_notes_wallet_default_product",
        domain="[('type', '=', 'service')]",
    )
