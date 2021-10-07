# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


# TODO: Remove when migrating to next version
def _rename_cagnotte(env):
    if not openupgrade.column_exists(env.cr, "sale_order_line", "account_cagnotte_id"):
        return
    columns = {
        "sale_order_line": [
            ("account_cagnotte_id", "account_wallet_id"),
        ],
    }
    openupgrade.rename_columns(env.cr, columns)


def pre_init_hook(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _rename_cagnotte(env)
