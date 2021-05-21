from odoo import api, SUPERUSER_ID
from odoo import tools
from odoo.modules.module import get_module_resource


def _load_demo(env):

    def load_file(env, module, *args):
        tools.convert_file(
            env.cr, 'account_wallet',
            get_module_resource(module, *args), {}, 'init', False, 'demo')
    load_file(env, 'account_wallet', 'demo', 'ir_sequence.xml')
    load_file(env, 'account_wallet', 'demo', 'account_journal.xml')
    load_file(env, 'account_wallet', 'demo', 'account_account.xml')
    load_file(env, 'account_wallet', 'demo', 'account_wallet_type.xml')


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        wallet = env["ir.module.module"].search([
            ("name", "=", "account_wallet")])
        l10n_generic = env["ir.module.module"].search([
            ("name", "=", "l10n_generic_coa"), ("state", "=", "installed")])
        if l10n_generic and wallet.demo:
            _load_demo(env)
