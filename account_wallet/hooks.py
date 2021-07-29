from odoo import api, SUPERUSER_ID
from odoo import tools
from odoo.modules.module import get_module_resource
from openupgradelib import openupgrade


def _load_demo(env):

    def load_file(env, module, *args):
        tools.convert_file(
            env.cr, 'account_wallet',
            get_module_resource(module, *args), {}, 'init', False, 'demo')
    load_file(env, 'account_wallet', 'demo', 'ir_sequence.xml')
    load_file(env, 'account_wallet', 'demo', 'account_journal.xml')
    load_file(env, 'account_wallet', 'demo', 'account_account.xml')
    load_file(env, 'account_wallet', 'demo', 'account_wallet_type.xml')


def _rename_cagnotte(env):
    """
        As module has changed its name, we migrate columns here
    :param env: [description]
    :type env: [type]
    """
    if not openupgrade.column_exists(env.cr, "cagnotte_type"):
        return
    tables = [
        ("cagnotte_type", "account_wallet_type"),
        ("account_cagnotte", "account_wallet"),
    ]
    openupgrade.rename_tables(env.cr, tables)
    columns = {
        "account_wallet": [
            ("cagnotte_type_id", "wallet_type_id"),
            ("solde_cagnotte", "balance"),
        ],
        # Field on account_move coming from former account_invoice should
        # be migrated manually - Keep for record
        # "account_move": [
        #     ("cagnotte_type_id", "account_wallet_type_id"),
        # ],
        "account_move_line": [
            ("account_cagnotte_id", "account_wallet_id"),
        ]
    }
    openupgrade.rename_columns(env.cr, columns)


def pre_init_hook(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _rename_cagnotte(env)


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        wallet = env["ir.module.module"].search([
            ("name", "=", "account_wallet")])
        l10n_generic = env["ir.module.module"].search([
            ("name", "=", "l10n_generic_coa"), ("state", "=", "installed")])
        if l10n_generic and wallet.demo:
            _load_demo(env)
