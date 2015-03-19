# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Nemry Jonathan
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
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _ 

from tempfile import NamedTemporaryFile
import smtplib
import email.encoders
from email.mime import text

#Constant of the Mail message
MAIL_CONTENT = """
<p>
    <b>
        This is a CV update request.
    </b>
</p>
Would you please review your cv in attachment and complete
it with at least your latest experience and/or any information you may find
relevant.
<br/>
For this purpose, you must use the Europass application available 
here: <b>http://europass.cedefop.europa.eu/fr/documents/curriculum-vitae</b>
by loading this file into the application.
<br/>
Once your work done, click on "save" 
and send the PDF+XML format to the following address: 
<b>hrEuropass@gmail.com</b>
<br/>
Thank you very much.
<br/>
<br/>
Your CV administrator.
<br/>
<br/>
<b>PLEASE DO NOT REPLY</b> to this email.
This email message was sent from a notification-only email address 
that cannot accept incoming email.
"""

class hr_europass_cv_send_mail(osv.Model):


    """
    # hr_europass_cv_send_mail
    # class of the model wizard, made to give access of user to send "update 
    # request" to an other user via mail
    # mail can contain a text by default or not depending the choice of 
    # the user
    """
    
    def action_cancel(self, cr, uid, ids, context=None):
        """
        # action_cancel return to the model user before the opening of the 
        # wizard
        """
        return {'type':'ir.actions.act_window_close'}
    """
    # 
    """
    def send_xml_by_mail(self, cr, uid, ids, context=None):
        record_id = context and context.get('active_id', False) or False
        if record_id:
            #we start getting the cv information
            cv_model = self.pool.get('hr.europass.cv').browse(cr,
                                                              uid,
                                                              record_id,
                                                              context=context)
            #next step is to get the data encoded
            wizardContain = self.browse(cr, uid, ids, context=context)
            file_pdf = NamedTemporaryFile(delete=False)
            text = cv_model.cv.decode('base64')
            file_pdf.write(text)
            fileName = cv_model.fname
            content = ""
            content = content + wizardContain[0].content
            addressDestination = wizardContain[0].addressDest
            content = content.encode('utf-8')

            #initialisation of the parameters to connect to email address
            SMTP_SERVER = 'smtp.gmail.com'
            SMTP_PORT = 587
            sender = 'hrEuropass@gmail.com'
            password = 'hrEuro123456'
            session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

            # create html email
            to = [addressDestination]
            subject = "Open ERP CV"
            html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 
                    Transitional//EN" '''
            html += '''"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional
                        .dtd"><html xmlns="http://www.w3.org/1999/xhtml">'''
            html += '<body style="font-size:12px;font-family:Verdana"><p>'
            html += content + '</p>'
            html += "</body></html>"
            emailMsg = email.MIMEMultipart.MIMEMultipart('alternative')
            emailMsg['Subject'] = subject
            emailMsg['From'] = sender
            emailMsg['To'] = ', '.join(to)
            emailMsg.attach(email.mime.text.MIMEText(html, 'html'))
            # now attach the file
            fileMsg = email.mime.base.MIMEBase('application', 'pdf')
            fileMsg.set_payload(text)
            email.encoders.encode_base64(fileMsg)
            fileMsg.add_header('Content-Disposition', 'attachment;filename='\
                                + fileName)
            emailMsg.attach(fileMsg)
            #================================================================
            session.ehlo()
            session.starttls()
            session.ehlo
            session.login(sender, password) 
            session.sendmail(sender, to, emailMsg.as_string())
            session.quit()
            
        ids = self.pool.get("hr.europass.cv.sendmail").search(cr,uid,
                            [('id','!=',-1)],context=None)
        self.unlink(cr,uid,ids,context=None)
        
        return False

    def get_text(self, cr, uid, ctx):
        """
        # get_text : obtains the variable MAIL_CONTENT
        """
        return MAIL_CONTENT

    def onchange_content(self, cr, uid, ids, changeContent):
        """
        # onchange_content: when user click, add or remove default text
        # if there is a text: then it remove it
        # if there is no text, then add it
        """
        v = {}
        if not changeContent:
            v['content'] = ""
        else:
            v['content'] = MAIL_CONTENT
            
        return {'value':v}
    
    _name = 'hr.europass.cv.sendmail'
    _columns = {
               'id':fields.integer(),
               'addressDest': fields.char(string=""""Recipient's email address""",
                                           size=128, required="True"),
               'content': fields.text(string="Message"),
               'changeContent' :  fields.boolean(string="""Automatic text
                for CV update"""),
              }
    _defaults = {
               'changeContent':True,
               'content':get_text,
               }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
