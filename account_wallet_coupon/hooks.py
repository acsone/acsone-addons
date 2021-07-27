# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def _move_coupons(env):
    if not openupgrade.column_exists(
            env.cr, "account_wallet", "coupon_code"):
        return
    query = """
        SELECT id, coupon_code
            FROM account_wallet
            WHERE coupon_code IS NOT NULL
    """
    env.cr.execute(query)
    records = env.cr.fetchall()
    coupon_obj = env["coupon.coupon"]
    wallet_obj = env["account.wallet"]
    codes = {}
    for record in records:
        codes[record[0]] = record[1]
    for id, code in codes.items():
        coupon = coupon_obj.create({"code": code})
        wallet_obj.browse(id).coupon_id = coupon

    openupgrade.drop_columns(env.cr, [("account_wallet", "coupon_code")])      


def post_init_hook(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _move_coupons(env)
