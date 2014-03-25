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
from openerp import tools
import openerp
from types import NoneType
import urllib


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def companywebInformation(self, cr, uid, ids, context=None, vat_number=None):
       
        endOfActivity = False
        score = "12"
        endDate = "0"
        if (endDate == "0"):
            endDateTxt = "__/__/____"
        else:
            yearOfEndDate = endDate[0:4]
            monthOfEndDate = endDate[4:6]
            dayOfEndDate = endDate[6:]
            endDateTxt = dayOfEndDate + "/" + monthOfEndDate + "/" + yearOfEndDate
            endOfActivity = True
        
        warningstxt = "- Baisse du crédit client et hausse du crédit fournisseur  (2004)   (2008)   (2012)  \n - Warnings de certaines filiales"
        
        if (endOfActivity == True):
            fichier = "barometer_stop.png"
            im = urllib.urlopen('http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        elif (score != False):
            if (score[0] == '-'):
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
            im = urllib.urlopen('http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        else:
            fichier = "barometer_none.png"
            img_path = openerp.modules.get_module_resource('account_companyweb', 'images/barometer', fichier)
            with open(img_path, 'rb') as f:
                source = f.read()
 
        image = tools.image_resize_image_medium(source.encode('base64'))
        
        vatc = "BE" + vat_number
        res_partner_model = self.pool.get("res.partner")
        partner_ids = res_partner_model.search(cr,uid,[('vat','=',vatc)],context=context)
        partner = res_partner_model.browse(cr,uid,partner_ids)[0]
        
        valeur = {
                  'name': partner.name + ", SA",
                  'vat_number': partner.vat[3:],
                  'street': partner.street,
                  'zip': partner.zip,
                  'city': partner.city,
                  'creditLimit': "661000",
                  'startDate': "04/10/1994",
                  'endDate': endDateTxt,
                  'image': image,
                  'warnings': warningstxt,
                  'url': "http://www.google.be",
                  'vat_liable': True,
                  'equityCapital': "6268475" + " (2012)",
                  'addedValue': "5346739" + " (2012)",
                  'turnover': "11420352" + " (2012)",
                  'result': "741894" + " (2012)",
                  }
        wizard_id = self.pool.get('account.companyweb.wizard').create(cr, uid, valeur, context=None)

        return {
            'name': "Informations CompanyWeb.be",
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

    """def companywebInformation(self, cr, uid, ids, context=None, vat_number=None):
        try:
            from lxml import etree
        except:
            raise osv.except_osv(
                'Warning !', 'Please download python lxml module from\nhttp://lxml.de/index.html#download\nand install it')

        login = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'companyweb.login', False)
        print login
        pswd = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'companyweb.pswd', False)
        print pswd
        url = "http://odm.outcome.be/alacarte_onvat.asp?login=" + \
            login + "&pswd=" + pswd + "&vat=" + vat_number + "&lang=1"
        print url
        tree = etree.parse(url)

        if (tree.xpath("/Companies")[0].get("Message") != ""):
            raise osv.except_osv(
                'Error!', "Bad login or password.\nPlease configure it in settings/configuration/companyWeb.be\nor contact companyweb BVBA/SPRL")
        elif (tree.xpath("/Companies")[0].get("Count") == "0"):
            raise osv.except_osv(
                'Warning !', "VAT number of this company is not register on companyWeb.be database")

        firm = tree.xpath("/Companies/firm")

        startDate = firm[0].xpath("StartDate")[0].text
        formatStartDate = startDate[6:] + "/" + \
            startDate[4:6] + "/" + startDate[0:4]

        endOfActivity = False

        endDate = firm[0].xpath("EndDate")[0].text
        if (endDate == "0"):
            endDateTxt = "__/__/____"
        else:
            yearOfEndDate = endDate[0:4]
            monthOfEndDate = endDate[4:6]
            dayOfEndDate = endDate[6:]
            endDateTxt = dayOfEndDate + "/" + \
                monthOfEndDate + "/" + yearOfEndDate
            endOfActivity = True

        warningstxt = ""
        for warning in firm[0].xpath("Warnings/Warning"):
            warningstxt = warningstxt + "- " + warning.text + "\n"

        if (endOfActivity == True):
            fichier = "barometer_stop.png"
            im = urllib.urlopen(
                'http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        elif (len(firm[0].xpath("Score")) > 0):
            score = firm[0].xpath("Score")[0].text
            if (score[0] == '-'):
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

        if (len(firm[0].xpath("Balans/Year")) > 0):
            year = firm[0].xpath("Balans/Year")[0].get("value")
            for Element2 in firm[0].xpath("Balans/Year")[0]:
                if (not isinstance(Element2.text, NoneType)):
                    dicoRoot[Element2.tag] = Element2.text + ' (' + year + ')'

        def getValue(attr):
            if (attr not in dicoRoot) or (isinstance(dicoRoot[attr], NoneType)):
                return "N/A"
            else:
                return dicoRoot[attr]

        if (getValue('VATenabled') == "True"):
            VATenabled = True
        else:
            VATenabled = False

        valeur = {
            'name': getValue('Name') + ", " + getValue('JurForm'),
            'vat_number': getValue('Vat'),
            'street': getValue('Street') + ", " + getValue('Nr'),
            'zip': getValue('PostalCode'),
            'city': getValue('City'),
            'creditLimit': getValue('CreditLimit'),
            'startDate': formatStartDate,
            'endDate': endDateTxt,
            'image': image,
            'warnings': warningstxt,
            'url': dicoRoot['Report'],
            'vat_liable': VATenabled,
            'equityCapital': getValue('Rub10_15'),
            'addedValue': getValue('Rub9800'),
            'turnover': getValue('Rub70'),
            'result': getValue('Rub9904'),
        }

        wizard_id = self.pool.get('account.companyweb.wizard').create(
            cr, uid, valeur, context=None)

        return {
            'name': "Informations CompanyWeb.be",
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
        }"""

    def button_companyweb(self, cr, uid, ids, context=None):

        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.vat:
                raise osv.except_osv(
                    'Error!', "This company has no VAT number")
            vat = partner.vat

        vat_country = vat[:2].lower()
        vat_number = vat[2:].replace(' ', '')

        if (vat_country == "be"):
            return self.companywebInformation(cr, uid, ids, context, vat_number)
        else:
            raise osv.except_osv(
                'Error!', "CompanyWeb.be is only available for companies which have a Belgian VAT number")


res_partner()
