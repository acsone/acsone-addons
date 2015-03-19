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
from openerp.osv import osv, fields
from tempfile import TemporaryFile
from openerp.tools.translate import _
import logging
import time
import datetime
import pytz
import traceback
from datetime import datetime
from hr_europass_library.hr_europass_library import hr_europass_language \
    as myDictionaryLanguage
from hr_europass_library.hr_europass_library import hr_europass_xml \
    as myParser
from hr_europass_library.hr_europass_library import hr_europass_pdf_extractor
from hr_europass_library.hr_europass_library import hr_europass_report\
    as objReport
from hr_europass_library.hr_europass_library_update import master_update\
    as controller


"""
#
# This class is the main class.
#
# CV model is the representation of one CV. The CV is a PDF that contains XML.
# It's format is the architecture of Europass xml.
"""


class cv(osv.Model):

    def get_fields_value(self, vals):

        """
        # "vals" is a dictionary
        # this method return the dictionary completed with the necessary
        # values of the model CV. It means:
        # -id_model
        # -first_name
        # -surname
        # -language
        # -text
        # -name
        #
        # pre: vals is instantiated and contains an Europass CV that contains
        #     the xml who contains itself the necessary data
        # post: vals is modified and key adding for return
        #        exception "Invalid Europass PDF" is rased if the XML is not
        #        valid
        # res: val
        """

        try:
            #first decode the database field into pdf content
            content = vals['cv'].decode('base64')
            xml = self.get_xml_from_pdf(content)
            #second: parsing the XML
            myObjXml = myParser(xml)
            myObjXml._readXml(True)
            #next step: getting data into "vals" from the object
            vals['id_model'] = myObjXml._getIdModel()
            vals['first_name'] = myObjXml.first_name
            vals['surname'] = myObjXml.last_name
            findLanguage = myDictionaryLanguage()
            vals['language'] = \
                findLanguage.getLanguageFromAbstractWord(myObjXml.language)
            vals['text'] = myObjXml.text
            vals['name'] = myObjXml.first_name + ' ' + myObjXml.last_name
        except:
            traceback.print_exc()
            raise osv.except_osv(_('Error'), _("Invalid Europass PDF"))
        return vals

    def set_html(self, cr, uid, with_current, current, id_to_delete):

        """
        # set_html ll set the html of the consistency for all the CV whom have
        # the same name
        #
        # pre:database,uid
        #     with_current : if the CV current must be into the search
        #     current: the CV current
        # post: id of consistency is updating for all CV of the search
        #       this search is made with or without current
        #       depending of with_current
        # NOTE: only the cv with state to "confirm" are including into
        #        the research
        # res: /
        """

        #first, obtains the name of current to make the research on it
        name = current[0].name
        """
        # depending of "with_current",
        # include or not the current id into the search
        # not including current means that we maybe have a list of ids to
        # delete, in that case, search ids MUST NOT contains ids to del
        """
        if not with_current:
            """
            # WARNING!! if current is the only
            # one with this name, result ll be NULL
            """
            second_search = []
            ids_to_update = self.search(cr, uid, [('name', '=', name),
                                                  ('state', '=', 'confirm'),
                                                  ('id', '!=', current[0].id)],
                                        context=None)
            if len(id_to_delete) > 1:                
                #ids are the id to update
                for id_current in ids_to_update:
                    to_update = True
                    for id_del in id_to_delete:
                        if id_del == id_current:
                            to_update = False
                            break
                    if to_update:
                        second_search.append(id_current)
            else:
                second_search = ids_to_update
        else:
            second_search = self.search(cr, uid, [('name', '=', name),
                                                  ('state', '=', 'confirm')],
                                        context=None)
        #if list length is not 0
        if second_search:
            #get all CV from the ids
            same_cv_id = self.read(cr, uid, second_search,
                                   ['cv', 'ref_consistency'])
            id_ref_none, id_to_update = self.request_update(cr, uid,
                                                            current[0].name,
                                                            same_cv_id)
            if id_ref_none:
                super(cv, self).write(cr, uid, id_ref_none,
                                      {'ref_consistency': id_to_update},
                                      context=None)

    def open_europass(self, cr, uid, ids, context):
        """
        # Open Europass into browser
        """
        return {
        'type': 'ir.actions.act_url',
        'url': "https://europass.cedefop.europa.eu/editors/en/cv/compose",
        'target': 'new',
        }

    def request_update(self, cr, uid, name, all_cv):
        """
        # request_update ll return id of the consistency and list of id to add
        # this consistency id
        # if no consistency found for name (name is the "key") then create it
        #
        # pre: database, user, name, all_cv
        #        all_cv is a list of id, this list is sure not None(verified
        #        before calling)
        # post: depending the existing consistency or not, create it or not
        #         if a CV found with no ref_consistency and the name "name"
        #         then this CV ll be returned
        # res: id of consistency and list id of CV with no consistency and the
        #         name "name"
        """
        id_consistency = \
            self.pool.get('hr.europass.consistency').search(cr,
                                                            uid, [('name',
                                                            '=', name)])
        #request'll stock all xml file
        request = []
        id_ref_none = []
        id_cons_to_update = None
        my_obj_report = objReport()
        for cv_request in all_cv:
            content = cv_request['cv'].decode('base64')
            xml = self.get_xml_from_pdf(content)
            request.append(xml)
            if not cv_request['ref_consistency']:
                id_ref_none.append(cv_request['id'])

        if request:
            l_i, w_e, ed, sk = my_obj_report.manage_list_cv(request)
            values = {
                    'info_learner': l_i,
                    'work_experiences': w_e,
                    'skills': sk,
                    'educations': ed
                      }
            if not id_consistency: 
                values['name'] = name
                id_cons_to_update = \
                 self.pool.get("hr.europass.consistency").create(cr,
                                                                  uid, values)
            else:
                id_cons_to_update = id_consistency[0]
                self.pool.get('hr.europass.consistency').write(cr,
                                             uid, id_consistency[0], values)

        return id_ref_none, id_cons_to_update 

    def check_consistency(self, cr, uid, ids, context=None):
        """
        # check the consistency between all CV with the same name and
        # a various language
        # this method was created to "test" the consistency with a button that
        # called it from the xml view. So it just call an other method
        #
        # database, user and id current
        """
        current = self.browse(cr, uid, ids, context=None)      
        self.set_html(cr, uid, True, current, ids)
    
    def update_request_report(self, cr, uid, ids, context=None):
        """
        # update_request_report: request to update and generate a report
        #                         based on the draft and the right version
        #
        """
        my_ctrl = controller()
        current = self.browse(cr, uid, ids, context=None)

        #get xml from the right version
        content = current[0].cv.decode('base64')
        xml_right = self.get_xml_from_pdf(content)

        #get xml from the draft version
        content = current[0].temp.decode('base64')
        xml_draft = self.get_xml_from_pdf(content)

        #send to library to get the html

        report = my_ctrl.get_report_xml(xml_draft, xml_right)
        html = my_ctrl.get_html_from_xml(report)

        super(cv, self).write(cr, uid, current[0].id, {'report_update':html} ,
                               context=context)

    def get_xml_from_pdf(self, content):
        """
        # return xml from conten, content is a Europass v3 PDF
        """
        fileTemp = TemporaryFile()
        fileTemp.write(content)
        fileTemp.seek(0)
        pdf = hr_europass_pdf_extractor()
        xml = pdf._return_xml_from_pdf(fileTemp) 
        return xml
    """
    # METHOD : management WORKFLOW
    """
    def confirm(self, cr, uid, ids, context={}):
        """
        # confirm is method using for WORKFLOW
        # it put the state field, as its name says,in "confirm"
        #
        # pre: database, uid and ids
        # post: rewrite of the current object with the modification
        #       calling the method set_html for updating the consistency
        # WARNING: set_html MUST be called AFTER the write, because ONLY the
        # confirmed state are include into the consistency
        """
        current = self.browse(cr, uid, ids, context=None)
        values = {
                  'state':"confirm",
                  'last_update': datetime.now()
                 }
        super(cv, self).write(cr, uid, current[0].id, values , context=context)
        self.set_html(cr, uid, True, current, ids)
        print "ok"

    def confirm_draft(self, cr, uid, ids, context={}):
        """
        # confirm_draft is used to confirm a draft CV.
        # draft CV is the pdf Europass v3 saving into the temp field
        # right CV is the pdf Europass v3 saving into the cv field
        # confirm draft ll put temp field into cv field and removing temp after
        # work done
        #
        # pre: database, cr, uid and context as always
        # post: modification of the current CV who ll be changed by its field
        #        cv and temp
        # WARNING: this action include all restriction presents into a create
        #         or write, and its include too the fact that the CV can not 
        #         change its name. Raise an exception if the update field 
        #         try to change it
        # res:/
        """
        current = self.browse(cr, uid, ids, context=None)

        #just initialize the dictionary for knowing what it will contain
        values = {
                  'cv':current[0].temp,
                  'fname':current[0].fname_temp,
                  'temp':None,
                  'fname_temp':"None",
                  'id_model':None,
                  'first_name':None,
                  'surname':  None,
                  'language':None,
                  'text':None,
                  'name':None,
                  'report_update':"None",
                  'last_update': datetime.now()
                 }

        #obtaining the values
        values = self.get_fields_value(values)
        if values['name'] != current[0].name:
            raise osv.except_osv(_('Error'), _("""Impossible to make an update
             to CV with different name"""))
        else:
            super(cv, self).write(cr, uid, current[0].id, values ,
                                   context=context)
            current = self.browse(cr, uid, ids, context=None)
            self.set_html(cr, uid, True, current, ids)

    def refuse(self, cr, uid, ids, context=None):
        """
        # refuse a draft
        # remove the pdf from the field (and from the database in the same
        # occasion. The state ll be in confirm again
        #
        # pre: database, id user and id current
        # post: current is modify and temp file is removed, state in confirm
        # res: True or False depending of the super write
        """
        current = self.browse(cr, uid, ids, context=None)
        values = {
                  'temp':None,
                  'fname_temp':"None",
                  'state':"confirm",
                  'report_update':None,
                }
        return super(cv, self).write(cr, uid, current[0].id, values ,
                                      context=context) 


    def refuse_new(self, cr, uid, ids, context=None):
        """
        # refuse to create a CV.
        # CV after creation, CV ll be into new, manager has to accept it, more
        # specifically confirm it
        # this confirmation is different that the draft confirmation, so
        # refuse it equals putting state to refuse.
        """
        current = self.browse(cr, uid, ids, context=None)
        values = {
                  'state':"refuse"
                }
        super(cv, self).write(cr, uid, current[0].id, values , context=context)
    """
    # HERE START: method Open ERP
    # create
    # write
    # unlink
    """

    def create(self, cr, uid, vals, context=None):
        """
        # Create
        # 
        # Receive a PDF from the binary field named 'cv'
        # call the method 'getFieldsValue(vals)'. The objective is to
        # get all the fields value like name etc from the XML into
        # the PDF.An exception ll be raise too if the PDF is not a
        # Europass v3 format
        # 
        # pre: Open ERP data like database, connexion AND values
        # post: save a new model with all data into database
        #       raise error if not right format
        # res: id of the new object, nothing if it failed
        """

        if "pdf" in vals['fname']:
            vals = self.get_fields_value(vals)
            vals['last_update'] = datetime.now()
            vals['state'] = "new"
            if vals['first_name'] == "" or vals ['surname'] == "":
                raise osv.except_osv(_('Error'), _("No name and/or surname"))
            res = super(cv, self).create(cr, uid, vals , context=context)  
        else:
            raise osv.except_osv(_('Error'), _("""Only Europass PDF-XML
             are accepted"""))
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        # Write
        # 
        # Receive a PDF from the binary field named 'cv'
        # call the method 'getFieldsValue(vals)'. The objective is to
        # get all the fields value like name etc from the XML into the PDF
        # An exception 'll be raise too if the PDF is not a Europass v3 format
        #
        # pre: Database connexion,id model, vals to update and context to None
        # post: model with ids is modified and data updated.
        #       WARNINGS: vals MUST contain a PDF Europass v3 OR MUST have the
        #       field
        #                 'employee_ref' other case, impossible to make update
        #                Other point: the 'state' value of the current CV MUST
        #                 NOT be "refuse"
        #                 if it is, raise an exception
        # res: True if update is made, False other cases
        """
        current = self.browse(cr, uid, ids, context=None)
        values = vals
        res = False
        if current[0].state == "refuse":
                raise osv.except_osv(_('Error'), _("Must confirm before edit"))
        else:
            if "cv" in vals:   
                try:
                    current = self.browse(cr, uid, ids, context=None)
                    content = vals['cv'].decode('base64')   
                    xml = self.get_xml_from_pdf(content)
                except:
                    traceback.print_exc()
                    raise osv.except_osv(_('Error'), _("Invalid Europass PDF"))
                
                myObjXml = myParser(xml)
                myObjXml._readXml(False)
                new_id = myObjXml._getIdModel()
                fnameNew = new_id + ".pdf"
                if new_id != current[0].id_model:
                    raise osv.except_osv(_('Error'), _("""Impossible to 
                        make an update CV with CV that have different name
                        and/or different language"""))
                else:
                    values = {
                                'cv':current[0].cv,
                                'fname':current[0].fname,
                                'temp':vals['cv'],
                                'fname_temp':fnameNew,
                                'state':'draft',
                              }
                    if "employee_ref" in vals:
                        values['employee_ref'] = vals['employee_ref']
                    if "note" in vals:
                        values['note'] = vals['note']
            res = super(cv, self).write(cr, uid, ids, values ,
                                             context=context)
                
        return res
    def unlink(self, cr, uid, ids, context=None):
        """
        # Unlink
        #
        # before delete the current model, we have to update the version 
        # of the consistency for this CV
        #
        # pre: database connection, id user, id current model
        # post: this model is deleted from the database
        # res: True if deleted, false if not
        # Warning!! if deleted CV are the last, we have to remove the 
        # consistency of the database
        """
        current = self.browse(cr, uid, ids, None)
        array_to_check = []
        for one in current:
            first_name = one.name
            find = False
            for el in array_to_check:
                if el.name == first_name:
                    find = True
                    break
            if not find:
                array_to_check.append(one)
        for to_check in array_to_check:        
            name = to_check.name
            other_ask = self.search(cr, uid, [('name', '=', name),
                                              ('state', '=', 'confirm'),
                                              ('id', '!=', ids)],
                                               context=None)
            if not other_ask:
                id_consistency = \
                self.pool.get('hr.europass.consistency').search(cr, uid,
                                                            [('name', '=',
                                                               name)])
                if id_consistency:
                    self.pool.get("hr.europass.consistency").unlink(cr,
                                                            uid,
                                                             id_consistency)
            else:
            #call the update version
                self.set_html(cr, uid, False, current, ids)
        #update is made,now delete
        return super(cv, self).unlink(cr, uid, ids)

    _name = 'hr.europass.cv'
    _logger = logging.getLogger(_name)
    _columns = {
                'id':fields.integer(),
                'id_model': fields.char(string="Model_ID", size=128),
                'text': fields.text(string="CV content"),
                'name': fields.char(string="Name", size=128, readonly="True"),
                'first_name': fields.char(string="First name", size=128,
                                          readonly="True"),
                'surname': fields.char(string="Surname", size=128,
                                        readonly="True"),
                'cv': fields.binary("Europass CV", filters='*.pdf',
                                     required="True"),
                'website': fields.char(string="Europass" , readonly="True"),
                'fname': fields.char('File Name', size=256),
                'language': fields.char('Language', size=256, readonly="True"),
                'last_update': fields.datetime('Last update',
                                               size=256,readonly="True"),
                'state': fields.selection([('new', 'New'),
                                           ('draft', 'Draft'),
                                           ('confirm', 'Confirmed'),
                                            ('refuse', 'Refused')],
                                          'Status', readonly="True"),
                'temp' : fields.binary("Waiting to be confirmed",
                                        filters='*.pdf', readonly="True"),
                'fname_temp' :  fields.char("File name temp",
                                            size=256, readonly="True"),
                'note' : fields.text(),
                'render_matching_version': fields.text(string="""Report 
                                            consistency"""),
                'ref_consistency':fields.many2one('hr.europass.consistency',
                                                   'id'),
                'ref_info':fields.related('ref_consistency', 'info_learner',
                                           type='text', readonly="True"),
                'ref_w_e':fields.related('ref_consistency', 'work_experiences',
                                          type='text', readonly="True"),
                'ref_ed':fields.related('ref_consistency', 'educations',
                                         type='text', readonly="True"),
                'ref_sk':fields.related('ref_consistency', 'skills',
                                        type='text', readonly="True"),
                'report_update':fields.text(readonly="True"),
                'employee_ref':fields.many2one('hr.employee', 'Employee'),
                }
    _defaults = {
                 'name':"None",
                 'fname_temp':"None",
                 'website': """https://europass.cedefop.europa.eu/editors/en/
                            cv/compose""",
                 'ref_consistency':None,
                 'report_update':"None",
                 }
    _sql_constraints = [('id_model', 'unique(id_model)',
                         'Duplication prohibited ')]

"""    
# hr_europass_consistency
# -----------------------

# Model used to check the consistency between different language version
# It is implemented for having the same consistency between same CV

"""
class hr_europass_consistency(osv.Model):


    _name = 'hr.europass.consistency'
    _columns = {
                'id': fields.integer(),
                'name':fields.char(size=128, readonly="True"),
                'info_learner':fields.text(readonly="True"),
                'work_experiences':fields.text(readonly="True"),
                'educations':fields.text(readonly="True"),
                'skills':fields.text(readonly="True"),
                }

"""
# hrEuropassTrash: model for CV with wrong format
"""
class hr_europass_trash(osv.Model):


    _name = 'hr.europass.trash'
    _columns = {
            'file_name':fields.char('File name', size=256, readonly="True"),
            'file':fields.binary(string="File", readonly="True"),
            'write_date' : fields.datetime('Last update', readonly="True"),
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
