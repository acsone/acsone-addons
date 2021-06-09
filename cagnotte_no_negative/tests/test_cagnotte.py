# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.cagnotte_base.tests.common import CagnotteCommon
from odoo.exceptions import ValidationError


class TestCagnotteNegative(CagnotteCommon):

    @classmethod
    def setUpClass(cls):
        super(TestCagnotteNegative, cls).setUpClass()
        cls.account_model = cls.env["account.account"]
        cls.account_invoice_obj = cls.env["account.invoice"]
        cls.register_payments_model = cls.env['account.register.payments']
        cls.move_obj = cls.env["account.move"]
        cls.partner3 = cls.env.ref('base.res_partner_3')
        account_user_type = cls.env.ref(
            'account.data_account_type_receivable')
        cls.account_rec1_id = cls.account_model.create(dict(
            code="cust_acc",
            name="customer account",
            user_type_id=account_user_type.id,
            reconcile=True,
        ))
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in")
        # Create a cagnotte type with no negative constraint
        cls.cagnotte_type.no_negative = True
        vals = {
            'cagnotte_type_id': cls.cagnotte_type.id,
        }
        cagnotte = cls.cagnotte_obj.new(vals)
        cagnotte._onchange_cagnotte_type_id()
        cls.cagnotte_no_negative = cls.cagnotte_obj.create(
            cagnotte._convert_to_write(cagnotte._cache))

    def test_no_negative(self):
        """
            Provision cagnotte with 100.0
            Use cagnotte with 200.0
        """
        self._provision_cagnotte(100.0)
        account_id = self.cagnotte_no_negative.cagnotte_type_id.account_id.id
        journal_id = self.cagnotte_no_negative.cagnotte_type_id.journal_id.id
        vals = {
            "journal_id": journal_id,
            "line_ids": [
                (0, 0, {
                    "account_id": account_id,
                    "account_cagnotte_id": self.cagnotte_no_negative.id,
                    "name": "payment with my cagnotte",
                    "debit": 100
                }),
                (0, 0, {
                    "account_id": self.account_rec1_id.id,
                    "name": "payment with my cagnotte",
                    "credit": 100})]}
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.move_obj.create(vals)

        # Authorize negative cagnotte
        self.cagnotte_no_negative.no_negative = False
        self.move_obj.create(vals)
        self.assertTrue(self.cagnotte_no_negative.is_negative)

    def test_cagnotte_create_type(self):
        """
            Create a cagnotte from code specifying simply the type
        """
        vals = {
            'cagnotte_type_id': self.cagnotte_type.id,
        }
        cagnotte = self.cagnotte_obj.create(vals)
        self.assertTrue(cagnotte.no_negative)
