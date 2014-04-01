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

from openerp.osv import fields, orm


class account_companyweb_wizard(orm.TransientModel):

    _name = 'account.companyweb.wizard'
    _columns = {
        'vat_number': fields.text('VAT number', readonly=True),
        'name': fields.text('Name', readonly=True),
        'street': fields.text('Address', readonly=True),
        'zip': fields.text('Postal code', readonly=True),
        'city': fields.text('City', readonly=True),
        'creditLimit': fields.text('Credit limit', readonly=True),
        'startDate': fields.text('Start date', readonly=True),
        'endDate': fields.text('End date', readonly=True),
        'image': fields.binary('Health barometer', readonly=True),
        'warnings': fields.text('Warnings', readonly=True),
        'url': fields.char('Detailed Report', readonly=True),
        'vat_liable': fields.boolean("Subject to VAT", readonly=True),
        'equityCapital': fields.text('Equity Capital', readonly=True),
        'addedValue': fields.text('Gross Margin (+/-)', readonly=True),
        'turnover': fields.text('Turnover', readonly=True),
        'result': fields.text('Fiscal Year Profit/Loss (+/-)', readonly=True),
    }

    def update_information(self, cr, uid, ids, context):
        res_partner_model = self.pool.get('res.partner')
        partner_id = context['active_id']
        this = self.browse(cr, uid, ids)[0]
        res_partner_model.write(cr, uid, partner_id, {'name': this.name, 'street': this.street, 'city': this.city, 'zip': this.zip})
        if this.creditLimit and this.creditLimit != 'N/A':
            res_partner_model.write(cr, uid, partner_id, {'credit_limit': this.creditLimit})
        return True
