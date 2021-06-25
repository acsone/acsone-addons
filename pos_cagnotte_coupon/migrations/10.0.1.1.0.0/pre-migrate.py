# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _move_check_cagnotte(cr):
    query = """
        UPDATE cagnotte_type
            SET no_negative = True
            WHERE check_cagnotte_amount = True
    """
    openupgrade.logged_query(cr, query)
    query = """
        UPDATE account_cagnotte
            SET no_negative = True
            WHERE EXISTS (
                SELECT 1 FROM cagnotte_type 
                WHERE id = account_cagnotte.cagnotte_type_id 
                AND no_negative = True
            )
    """
    openupgrade.logged_query(cr, query)


def migrate(cr, version):
    _move_check_cagnotte(cr)
