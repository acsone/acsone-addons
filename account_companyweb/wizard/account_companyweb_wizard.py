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

from openerp.osv import fields, osv
import openerp


class account_companyweb_wizard(osv.osv_memory):

    _name = 'account.companyweb.wizard'
    _columns = {
        'vat_number': fields.char('VAT number :', 256, readonly=True),
        'name': fields.char('Name:', 256, readonly=True),
        'street': fields.char('Address:', 256, readonly=True),
        'zip': fields.char('', 256, readonly=True),
        'city': fields.char('', 256, readonly=True),
        'creditLimit': fields.char('Credit limit : ', 256, readonly=True),
        'startDate': fields.char('Start date : ', 256, readonly=True),
        'endDate': fields.char('End date : ', 256, readonly=True),
        'image': fields.binary('Health barometer : ', readonly=True),
        'warnings': fields.text('Warnings : ', 1028, readonly=True),
        'url': fields.char('', 256, readonly=True),
        'vat_liable': fields.boolean("Liable to VAT", readonly=True),
        'equityCapital': fields.char('Equity Capital : ', 256, readonly=True),
        'addedValue': fields.char('Added value : ', 256, readonly=True),
        'turnover': fields.char('Turnover : ', 256, readonly=True),
        'result': fields.char('Fiscal Year Profit (Loss) : ', 256, readonly=True),
    }

    def act_destroy(self, *args):
        return {'type': 'ir.actions.act_window_close'}

    def open_url_function(self, cr, uid, ids, context):
        url = self.browse(cr, uid, ids)[0].url
        if url:
            return {'type': 'ir.actions.act_url', 'url': url, 'nodestroy': True, 'target': 'new'}
        else:
            return True

    def update_information(self, cr, uid, ids, context):
        res_partner_model = self.pool.get('res.partner')
        this = self.browse(cr, uid, ids)[0]
        vat = "BE0" + this['vat_number']
        partners_ids = res_partner_model.search(
            cr, uid, [('vat', '=', vat)], context=context)
        for partner in res_partner_model.browse(cr, uid, partners_ids, context=context):
            res_partner_model.write(
                cr, uid, partner['id'], {'name': this.name, 'street': this.street, 'city': this.city, 'zip': this.zip})
            res_partner_model.write(cr, uid, partner['id'], {})
            #res_partner_model.write(cr,uid,partner['id'],{'credit_limit': this['creditLimit']})

account_companyweb_wizard()
