
from odoo import models
from odoo.models import BaseModel


class PosSession(models.Model):

    _inherit = "pos.session"

    def _get_statement_line_vals(
            self, statement, amount, payment=None, payment_method=None):
        """
            Transmit the Wallet from the POS order payment to the generated
            bank statement.
        """
        res = super()._get_statement_line_vals(
            statement, amount, payment=None, payment_method=None)
        if payment and payment.account_wallet_id:
            res.update({
                "account_wallet_id": payment.account_wallet_id.id,
            })
        return res

    def _get_sale_vals(self, key, amount, amount_converted):
        """ As key is a tuple that should not be different than the original,
            check if an account wallet is inside, take the value, then delete
            it from the tuple.
        """
        def test_wallet(value):
            return isinstance(value, BaseModel) and value._name == "account.wallet"
        account_wallet = self.env["account.wallet"]
        for key_value in key:
            if test_wallet(key_value):
                account_wallet = key_value
        if account_wallet:
            key = tuple(filter(lambda x: not test_wallet(x), key))
        res = super()._get_sale_vals(key, amount, amount_converted)
        if account_wallet:
            res.update({"account_wallet_id": account_wallet.id})
        return res

    def _get_sale_key(self, order_line, line):
        """
            Add an entry to the grouping key as we need to keep account move
            line for sale unique if there is a wallet linked to.
        """
        res = super()._get_sale_key(order_line, line)
        if order_line.account_wallet_id:
            res += (order_line.account_wallet_id,)
        return res
