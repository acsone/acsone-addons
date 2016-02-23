# -*- coding: utf-8 -*-
from openerp.tests import common
from openerp import fields


class TestAccountAnalyticProject(common.TransactionCase):

    def test_account_analytic_project(self):
        partner_id = self.env['res.partner'].create({
            'name': 'name',
        })
        vals = {
            'name': 'product_test_01',
            'lst_price': 2000.00,
        }
        product = self.env['product.product'].create(vals)
        sale_journal_id = self.env.ref('account.sales_journal')
        aai_id = self.ref('project.project_project_1')
        invoice_line = self.env['account.invoice.line'].create({
            'name': 'test',
            'account_id': self.ref('account.a_sale'),
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': product.id,
            'account_analytic_id': aai_id,
        })
        account_invoice = self.env['account.invoice'].create({
            'partner_id': partner_id.id,
            'account_id': self.ref('account.a_recv'),
            'journal_id': sale_journal_id.id,
            'date_invoice': fields.Date.today(),
            'invoice_line': [(6, 0, [invoice_line.id])],
        })
        self.assertTrue(
            account_invoice.account_analytic_id, 'Should have an account')
        self.assertEquals(
            account_invoice.account_analytic_id.id,
            aai_id,
            'Should have same account')
        invoice_line2 = self.env['account.invoice.line'].create({
            'name': 'test2',
            'account_id': self.ref('account.a_recv'),
            'price_unit': 2000.00,
            'quantity': 1,
            'product_id': product.id,
            'account_analytic_id': self.ref('project.project_project_2')
        })
        account_invoice.write({
            'invoice_line': [(4, invoice_line2.id)]
        })
        self.assertFalse(
            account_invoice.account_analytic_id, 'Should have an account')
