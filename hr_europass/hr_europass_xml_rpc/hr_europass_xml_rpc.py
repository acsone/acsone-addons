# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Nemry Jonthan
# Copyright (c) 2012 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import email
import imaplib
import time
from tempfile import TemporaryFile

import xmlrpclib
from hr_europass_library.hr_europass_library import hr_europass_xml as myParser
from hr_europass_library.hr_europass_library import hr_europass_pdf_extractor

"""
# Constant of the file
"""

MODEL = 'hr.europass.cv'
WRONG_MODEL = 'hr.europass.trash'
EXT = ".pdf"

#parameters to connect to Open ERP
USERNAME = 'admin'
PWD = 'admin'
DBNAME = "test"

#parameters to contect gmail
m = imaplib.IMAP4_SSL('imap.gmail.com', 993)
m.login('hrEuropass@gmail.com', 'hrEuro123456')
sock_common = xmlrpclib.ServerProxy('http://0.0.0.0:8069/xmlrpc/common')
uid = sock_common.login(DBNAME, USERNAME, PWD)
sock = xmlrpclib.ServerProxy('http://0.0.0.0:8069/xmlrpc/object')

def get_list_cv():

    """
    # get_list_cv
    # read email and get the CV find into this list
    # put the mail read into "UNSEEN" status
    """
    m.select() 
    resp, items = m.search(None, "UNSEEN")
    items = items[0].split()
    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        if mail.get_content_maintype() != 'multipart':
            continue
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            yield part.get_payload(decode=True), part.get_filename()

def get_id_from_xml(text):
    """
    # get_id_from_xml return the id model of the Open ERP CV model
    # it means the first name, surname and language of the CV
    # data are extracted from the xml itself extracted from the pdf
    """
    fileTemp = TemporaryFile()
    fileTemp.write(text)
    fileTemp.seek(0)
    pdf= hr_europass_pdf_extractor()
    text=pdf._return_xml_from_pdf(fileTemp) 
    myObjXml = myParser(text)
    try:
        myObjXml._readXml(False)
    except Exception:
        print Exception.args
    return myObjXml._getIdModel()

while True:

    """
    # loop of the xml rpc that ll scan the hrEuropass address mail
    # every 60s is the time between two scan
    # if CV are founded they are automatically sending to Open ERP
    """
    try:
        #after treatment, sleep 60s
        time.sleep(30)
        for element, fileName in get_list_cv():
            data = element.encode("base64")
            if "pdf" in fileName:
                idCV = get_id_from_xml(element)
                args = [('id_model', '=', idCV)]
                #first checking if the CV exist with this ID
                ids = sock.execute(DBNAME, uid, PWD, MODEL, 'search', args)
                fname = idCV + EXT
                #No ID found means that the CV is not yet created
                #so we have to
                if len(ids) == 0:
                    cv = {
                          'cv': data,
                          'fname':fname,
                          }
                    new_cv_id = sock.execute(DBNAME, uid,
                                              PWD, MODEL, 'create', cv)
                #other case means that the CV is found, so we have to update it
                else:
                    fields = ['state']
                    verifyCV = sock.execute(DBNAME,
                                             uid, PWD,
                                              MODEL, 'read'
                                              , ids, fields)
                    #CV that are already in state "new" or "refuse"
                    #are not updated
                    if verifyCV[0]['state'] != "new" \
                        and verifyCV[0]['state'] != "refuse":
                        cv = {
                              'cv': data,
                              'fname':fname,
                              }
                        result = sock.execute(DBNAME,
                                               uid, PWD, MODEL,
                                               'write', ids, cv)
    
            else:
                #here we have a wrong CV format
                wrongFormat = {
                    'file':data,
                    'file_name':fileName
                    }
                trash_id = sock.execute(DBNAME, uid,
                                         PWD, WRONG_MODEL, 'create',
                                          wrongFormat)
    except:
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

