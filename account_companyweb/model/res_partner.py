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

import urllib
import logging

from lxml import etree

from openerp.osv import orm
from openerp import tools
import openerp.modules


logger = logging.getLogger(__name__)


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def companyweb_information(self, cr, uid, ids, vat_number, context=None):
        login = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'companyweb.login', False)
        pswd = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'companyweb.pswd', False)
        url = "http://odm.outcome.be/alacarte_onvat.asp?login=" + \
            login + "&pswd=" + pswd + "&vat=" + vat_number

        if context.get('lang', '').startswith('fr'):
            url = url + "&lang=1"
        elif context.get('lang', '').startswith('nl'):
            url = url + "&lang=2"

        try:
            tree = etree.parse(url)
        except:
            logging.error("Error parsing companyweb url %s", url, exc_info=True)
            raise orm.except_orm('Warning !',
                                 "System error loading Companyweb data.\n"
                                 "Please retry and contact your "
                                 "system administrator if the error persists.")

        message = tree.xpath("/Companies")[0].get("Message")
        if message:
            raise orm.except_orm('Warning !',
                                 "Error loading Companyweb data:\n%s.\n"
                                 "\n"
                                 "Please check your credentials in settings/configuration/Companyweb.\n"
                                 "\n"
                                 "Login on www.companyweb.be with login 'cwacsone' and password 'demo' "
                                 "to obtain test credentials." % message)

        if tree.xpath("/Companies")[0].get("Count") == "0":
            raise orm.except_orm(
                'Warning !', "VAT number of this company is not known in the Companyweb database")

        firm = tree.xpath("/Companies/firm")

        startDate = firm[0].xpath("StartDate")[0].text
        endDate = firm[0].xpath("EndDate")[0].text
        if endDate == "0":
            endDate = False
            endOfActivity = False
        else:
            endOfActivity = True

        warningstxt = ""
        for warning in firm[0].xpath("Warnings/Warning"):
            warningstxt = warningstxt + "- " + warning.text + "\n"

        if endOfActivity:
            fichier = "barometer_stop.png"
            im = urllib.urlopen(
                'http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        elif len(firm[0].xpath("Score")) > 0:
            score = firm[0].xpath("Score")[0].text
            if score[0] == '-':
                signe = "neg-"
                if len(score) == 2:
                    chiffre = "0" + score[1:]
                else:
                    chiffre = score[1:]
            else:
                signe = "pos-"
                if len(score) == 1:
                    chiffre = "0" + score[0:]
                else:
                    chiffre = score[0:]

            fichier = signe + chiffre + ".png"
            im = urllib.urlopen(
                'http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        else:
            fichier = "barometer_none.png"
            img_path = openerp.modules.get_module_resource(
                'account_companyweb', 'images/barometer', fichier)
            with open(img_path, 'rb') as f:
                source = f.read()

        image = tools.image_resize_image_medium(source.encode('base64'))

        dicoRoot = dict()
        for Element in firm[0]:
            dicoRoot[Element.tag] = Element.text
        balance_year = ""
        if len(firm[0].xpath("Balans/Year")) > 0:
            balance_year = firm[0].xpath("Balans/Year")[0].get("value")
            for Element2 in firm[0].xpath("Balans/Year")[0]:
                if Element2.text:
                    dicoRoot[Element2.tag] = Element2.text

        def getValue(attr):
            return dicoRoot.get(attr, 'N/A')

        def getFloatValue(attr):
            r = dicoRoot.get(attr)
            if r:
                return float(r)
            else:
                return False

        valeur = {
            'name': getValue('Name'),
            'jur_form': getValue('JurForm'),
            'vat_number': "BE0" + getValue('Vat'),
            'street': getValue('Street') + ", " + getValue('Nr'),
            'zip': getValue('PostalCode'),
            'city': getValue('City'),
            'creditLimit': getFloatValue('CreditLimit'),
            'startDate': startDate,
            'endDate': endDate,
            'image': image,
            'warnings': warningstxt,
            'url': dicoRoot['Report'],
            'vat_liable': getValue('VATenabled') == "True",
            'balance_year': balance_year,
            'equityCapital': getFloatValue('Rub10_15'),
            'addedValue': getFloatValue('Rub9800'),
            'turnover': getFloatValue('Rub70'),
            'result': getFloatValue('Rub9904'),
        }

        wizard_id = self.pool.get('account.companyweb.wizard').create(
            cr, uid, valeur, context=None)

        return {
            'name': "Companyweb Informations",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.companyweb.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    def button_companyweb(self, cr, uid, ids, context=None):

        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.vat:
                raise orm.except_orm(
                    'Error!', "This company has no VAT number")
            vat = partner.vat

        vat_country = vat[:2].lower()
        vat_number = vat[2:].replace(' ', '')

        if vat_country == "be":
            return self.companyweb_information(cr, uid, ids, vat_number, context)
        else:
            raise orm.except_orm(
                'Error!', "Companyweb is only available for companies with a Belgian VAT number")
