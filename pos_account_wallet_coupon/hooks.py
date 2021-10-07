# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def _migrate_columns(env):
    """
    This is intended solely if former module was installed.
    """
    query = """
        SELECT id FROM ir_module_module WHERE name = 'pos_cagnotte_coupon'
    """
    env.cr.execute(query)
    if env.cr.fetchall():
        columns = {
            "account_bank_statement_line": [
                ("account_cagnotte_id", "account_wallet_id", "integer")
            ],
            "pos_order_line": [("account_cagnotte_id", "account_wallet_id", "integer")],
        }
        openupgrade.copy_columns(env.cr, columns)


def pre_init_hook(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _migrate_columns(env)
