# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo


def _recompute_solde_cagnotte(env):
    model = env['account.cagnotte']
    env.add_todo(model._fields['solde_cagnotte'], model.search([]))
    model.recompute()


def migrate(cr, version):
    if not version:
        return
    with odoo.api.Environment.manage():
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        _recompute_solde_cagnotte(env)
