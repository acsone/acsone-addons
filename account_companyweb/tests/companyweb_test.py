# -*- coding: utf-8 -*-
#
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import openerp.tests.common as common
from openerp import netsvc
import os
import logging

from openerp.tools import convert_xml_import
from openerp import tools

_logger = logging.getLogger(__name__)


def get_file(module_name, fp):
    pathname = os.path.join(module_name, fp)
    return tools.file_open(pathname)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


def load_data(cr, module_name, fp, idref=None, mode='init', noupdate=False, report=None):
    pathname = os.path.join(module_name, fp)
    fp = get_file(module_name, fp)
    _logger.info("Import datas from %s" % pathname)
    convert_xml_import(cr, module_name, fp, idref, mode, noupdate, report)


class companyweb_test(common.TransactionCase):

    def create_invoice(self, partner_id, date, amount):

        in_id = self.registry('account.invoice').create(self.cr, self.uid, {'reference_type': "none",
                                                                            'date_invoice': date,
                                                                            'partner_id': partner_id,
                                                                            'account_id': self.ref('account.a_recv'),
                                                                            'type': 'out_invoice',
                                                                            })

        self.registry('account.invoice.line').create(self.cr, self.uid, {'name': "xxx",
                                                                         'invoice_id': in_id,
                                                                         'account_id': self.ref('account.a_sale'),
                                                                         'price_unit': amount,
                                                                         'quantity': 1,
                                                                         })

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.uid, 'account.invoice', in_id, 'invoice_open', self.cr)

        return in_id

    def create_refund(self, partner_id, date, amount):

        in_id = self.registry('account.invoice').create(self.cr, self.uid, {'reference_type': "none",
                                                                            'date_invoice': date,
                                                                            'partner_id': partner_id,
                                                                            'account_id': self.ref('account.a_recv'),
                                                                            'type': 'out_refund',
                                                                            })

        self.registry('account.invoice.line').create(self.cr, self.uid, {'name': "xxx",
                                                                         'invoice_id': in_id,
                                                                         'account_id': self.ref('account.a_sale'),
                                                                         'price_unit': amount,
                                                                         'quantity': 1,
                                                                         })

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.uid, 'account.invoice', in_id, 'invoice_open', self.cr)

        return in_id

    def create_payment(self, date, amount, inv):
        voucher_id = self.registry('account.voucher').create(self.cr, self.uid, {
            'partner_id': inv.partner_id.id,
            'type': inv.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
            'account_id': self.ref('account.a_recv'),
            'date': date,
            'amount': amount,
        })

        voucher_browse = self.registry('account.voucher').browse(
            self.cr, self.uid, voucher_id)

        line = self.registry('account.voucher').recompute_voucher_lines(self.cr, self.uid, [voucher_id],
                                                                        voucher_browse.partner_id.id,
                                                                        voucher_browse.journal_id.id,
                                                                        voucher_browse.amount,
                                                                        voucher_browse.currency_id.id,
                                                                        voucher_browse.type,
                                                                        voucher_browse.date,
                                                                        context=None)
        line_cr = line['value']['line_cr_ids']

        line_cr_ids = list()

        for line in line_cr:
            data = dict()
            for key, value in line.items():
                data[key] = value
            data['voucher_id'] = voucher_id
            line_cr_ids.append(
                self.registry('account.voucher.line').create(self.cr, self.uid, data))

        self.registry('account.voucher').button_proforma_voucher(
            self.cr, self.uid, [voucher_id], context=None)

        voucher_browse = self.registry('account.voucher').browse(
            self.cr, self.uid, voucher_id)

        self.registry('account.move').post(
            self.cr, self.uid, [voucher_browse.move_id.id])

    def create_openSalesDoc(self, month, year):
        wizard_id = self.registry('account.companyweb.report.wizard').create(
            self.cr, self.uid, {'chart_account_id': 1, 'month': month, 'year': year}, context=None)
        self.registry('account.companyweb.report.wizard').create_openSalesDocs(
            self.cr, self. uid, [wizard_id])
        wizard = self.registry('account.companyweb.report.wizard').browse(
            self.cr, self.uid, wizard_id)

        import xlrd
        import tempfile
        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = wizard.data
        f = open(file_path, 'wb')
        f.write(data.decode('base64'))
        f.close()
        return xlrd.open_workbook(file_path)

    def create_createdSalesDoc(self, month, year):
        wizard_id = self.registry('account.companyweb.report.wizard').create(
            self.cr, self.uid, {'chart_account_id': 1, 'month': month, 'year': year}, context=None)
        self.registry('account.companyweb.report.wizard').create_createdSalesDocs(
            self.cr, self. uid, [wizard_id])
        wizard = self.registry('account.companyweb.report.wizard').browse(
            self.cr, self.uid, wizard_id)

        import xlrd
        import tempfile
        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = wizard.data
        f = open(file_path, 'wb')
        f.write(data.decode('base64'))
        f.close()
        return xlrd.open_workbook(file_path)

    def setUp(self):
        super(companyweb_test, self).setUp()
        company_id = self.ref('base.main_company')
        company_model = self.registry('res.company')
        company_model.write(self.cr, self.uid, company_id, {'vat': 'BE0477472701'})

    def test_created_doc_companyweb(self):
        date = '2014-01-01'
        amount = 1000
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, date, amount)

        invoice = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id)

        wb = self.create_createdSalesDoc("01", "2014")

        sheet = wb.sheet_by_index(0)

        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == invoice.number):
                trouve = True
                ligne = i
            i += 1

        self.assertTrue(trouve, "Invoice found in xls file")

        if (trouve):
            self.assertAlmostEqual(
                sheet.cell_value(ligne, 8), amount, 2, 'amount')
            self.assertEquals(sheet.cell_value(ligne, 4), "I", "docType")
            self.assertEquals(sheet.cell_value(ligne, 5), date, "date")

    def test_created_doc_diffrent_month_companyweb(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        invoice = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id)
        wb = self.create_createdSalesDoc("02", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == invoice.number):
                trouve = True
            i += 1

        self.assertFalse(trouve, "Invoice found in xls file")

    def test_open_doc_companyweb(self):
        date = '2014-01-01'
        amount = 1000

        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, date, amount)
        invoice = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id)
        wb = self.create_openSalesDoc("01", "2014")
        sheet = wb.sheet_by_index(0)

        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == invoice.number):
                trouve = True
                ligne = i
            i += 1

        self.assertTrue(trouve, "Invoice found in xls file")

        if (trouve):
            self.assertAlmostEqual(
                sheet.cell_value(ligne, 8), amount, 2, 'amount')
            self.assertEquals(sheet.cell_value(ligne, 4), "I", "docType")
            self.assertEquals(sheet.cell_value(ligne, 5), date, "date")
            self.assertEquals(sheet.cell_value(ligne, 4), "I", "docType")

    def test_open_doc_complete_reconcile_companyweb(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv = self.registry('account.invoice').browse(self.cr, self.uid, in_id)
        self.create_payment('2014-01-20', 1000, inv)
        wb = self.create_openSalesDoc("02", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == inv.number):
                trouve = True
            i += 1

        self.assertFalse(trouve, "Invoice found in xls file")

    def test_open_doc_partial_reconcile_1_companyweb(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv = self.registry('account.invoice').browse(self.cr, self.uid, in_id)
        self.create_payment('2014-01-20', 500, inv)
        wb = self.create_openSalesDoc("02", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == inv.number):
                trouve = True
            i += 1

        self.assertTrue(trouve, "Invoice found in xls file")

    def test_open_doc_partial_reconcile_2_companyweb(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv = self.registry('account.invoice').browse(self.cr, self.uid, in_id)
        self.create_payment('2014-01-20', 500, inv)
        self.create_payment('2014-02-20', 500, inv)
        wb = self.create_openSalesDoc("01", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == inv.number):
                trouve = True
            i += 1

        self.assertTrue(trouve, "Invoice found in xls file")

        wb = self.create_openSalesDoc("02", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == inv.number):
                trouve = True
            i += 1

        self.assertFalse
        (trouve, "Invoice found in xls file")

    def test_open_doc_openAmount(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv = self.registry('account.invoice').browse(self.cr, self.uid, in_id)
        self.create_payment('2014-01-20', 250, inv)
        self.create_payment('2014-02-20', 750, inv)
        wb = self.create_openSalesDoc("01", "2014")
        sheet = wb.sheet_by_index(0)
        trouve = False
        i = 1
        while (i < sheet.nrows) and (not trouve):
            if (sheet.cell_value(i, 3) == inv.number):
                trouve = True
                ligne = i
            i += 1

        self.assertTrue(trouve, "Invoice found in xls file")

        self.assertAlmostEqual(sheet.cell_value(ligne, 9), 750, 2, 'amount')

    def test_open_doc_custAcc(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id1 = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv1 = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id1)
        in_id2 = self.create_invoice(partner_id, '2014-01-01', 500)
        inv2 = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id2)

        wb = self.create_openSalesDoc("01", "2014")
        sheet = wb.sheet_by_index(0)
        i = 1
        ligne = list()
        while (i < sheet.nrows):
            if (sheet.cell_value(i, 3) == inv1.number or sheet.cell_value(i, 3) == inv2.number):
                ligne.append(i)
            i += 1

        self.assertAlmostEqual(
            sheet.cell_value(ligne[0], 10), 1500, 2, 'amount')
        self.assertAlmostEqual(
            sheet.cell_value(ligne[0], 10), sheet.cell_value(ligne[1], 10), 2, 'amount')

    def test_custAcc_refund(self):
        partner_id = self.registry('res.partner').create(self.cr, self.uid, {'name': 'test',
                                                                             'vat': 'BE0460392583',
                                                                             })
        in_id = self.create_invoice(partner_id, '2014-01-01', 1000)
        inv = self.registry('account.invoice').browse(
            self.cr, self.uid, in_id)

        self.create_refund(partner_id, '2014-02-02', 1000)

        wb = self.create_openSalesDoc("01", "2014")
        sheet = wb.sheet_by_index(0)
        i = 1
        while (i < sheet.nrows):
            if (sheet.cell_value(i, 3) == inv.number):
                ligne = i
            i += 1

        self.assertAlmostEqual(
            sheet.cell_value(ligne, 10), 1000, 2, 'amount')

        wb = self.create_openSalesDoc("02", "2014")
        sheet = wb.sheet_by_index(0)
        i = 1
        while (i < sheet.nrows):
            if (sheet.cell_value(i, 3) == inv.number):
                ligne = i
            i += 1

        self.assertAlmostEqual(
            sheet.cell_value(ligne, 10), 0, 2, 'amount')
