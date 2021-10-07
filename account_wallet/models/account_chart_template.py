# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from ..hooks import _load_demo


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        """
            We override this in order to integrate demo data
        """
        res = super()._load(
            sale_tax_rate=sale_tax_rate,
            purchase_tax_rate=purchase_tax_rate,
            company=company)
        account_wallet = self.env['ir.module.module'].search([
            ("name", "=", "account_wallet")])
        if account_wallet.demo:
            _load_demo(self.env)
        return res
