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
from lxml import etree as ET
from StringIO import StringIO
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream
import os

PATH_STYLE_ROOT = os.path.dirname(__file__) + "/../static/src/style/"


class hr_europass_xml:
    """
    # Hr europass xml 
    # using to parse an XML provided by Europass v3    # 
    """

    def __init__(self, textXML):
        self.textXML = textXML
        self.first_name = ""
        self.last_name = ""
        self.language = ""
        self.idCV = ""
        self.text = ""
        self.idModel = ""


    def _readXml(self, needText):
        """
        # put xml value into the necessary data
        # if need text is true, then put full text too
        """
        context = ET.iterparse(StringIO(self.textXML),
                                events=("start", "end"))
        root = None
        for event, elem in context:
            if event == "start" and root is None:
                root = elem    # the first element is root
                self.language = elem.attrib['locale']
            if event == "end":
                if "FirstName" in elem.tag:
                    if elem.text != None:
                        self.first_name = elem.text
                if "Surname" in elem.tag:
                    if elem.text != None:
                        self.last_name = elem.text
                if needText and elem.text != None:
                    self.text += elem.text

    def _getIdModel(self):
        """
        # return the concat of first_name_lastname_language
        """
        self.idModel = self.first_name + '_' + self.last_name + '_' + \
             self.language
        return self.idModel


class hr_europass_pdf_extractor:
    """
    # class using to extract the xml of the pdf europass v3
    """
    def _return_xml_from_pdf(self, fp):
        doc = PDFDocument()
        parser = PDFParser(fp)
        parser.set_document(doc)
        doc.set_parser(parser)
        # find the dictionary referencing the Eurpass XML Attachment
        for xref in doc.xrefs:
            for objid in xref.get_objids():
                obj = doc.getobj(objid)
                if isinstance(obj, PDFStream):
                    attrs = obj.attrs
                    subType = attrs.get("Subtype")
                    if subType is not None and subType.name == \
                        "application/xml":
                        return obj.get_data()


class hr_europass_language():
    
    """
    # class using to get the full language name from the abstract
    # if not define into the list, then it return the abstract one
    """
    
    def getLanguageFromAbstractWord(self, abstractLanguage):
        lanRetour = ""  
        if abstractLanguage == "en":
                lanRetour = "English"
        elif abstractLanguage == "nl" : 
                lanRetour = "Nederlands"
        elif abstractLanguage == "fr" : 
                lanRetour = "French"
        else :
            lanRetour = abstractLanguage

        return lanRetour 


class hr_europass_report():
    """
    # class using to generate the report
    # like a master class
    """
    L_I_PATH = PATH_STYLE_ROOT + "learner_info.xsl"
    W_E_PATH = PATH_STYLE_ROOT + "work_experience_list.xsl" 
    ED_PATH = PATH_STYLE_ROOT + "education_list.xsl"
    SK_PATH = PATH_STYLE_ROOT + "skills.xsl"

    def manage_list_cv(self, request_cv):
        """
        # pre:request_cv initialized. this is an array of xml 
        #    string CV
        #    this method 'll extract part of the CV
        #    more specifically :
        #    - WorkExperienceList
        #    - EducationList
        #    - Skills Computer
        # res: html of workexperience list
        #     html of education list
        #     html of skills
        """
        array_l_i = []
        array_w_e = []
        array_ed = []
        array_sk = []

        px = 90 / len(request_cv)
        px = "%s" % px
        for cv in request_cv:
            root_cv = ET.XML(cv)
            l_i, w_e, ed, sk = self.get_string(root_cv, px)
            array_l_i.append(l_i)      
            array_w_e.append(w_e)
            array_ed.append(ed)
            array_sk.append(sk)

        """ 
        # here all content are split and have right data
        # now we have to add every element parts to a root tag for each one
        """
        r_l_i = self.get_new_root_version()
        r_l_i = self.get_root_complete(array_l_i, r_l_i)
        r_w_e = self.get_new_root_version()
        r_w_e = self.get_root_complete(array_w_e, r_w_e)
        r_ed = self.get_new_root_version()
        r_ed = self.get_root_complete(array_ed, r_ed)
        r_sk = self.get_new_root_version()
        r_sk = self.get_root_complete(array_sk, r_sk)
        # now we have the three root parts
        # next step :  applied the xsl on each root into returns variables
        buffer_xml = self.get_string_representation(r_l_i)
        html_learner_info = self.transform(buffer_xml, self.L_I_PATH)
        buffer_xml = self.get_string_representation(r_w_e)
        html_work_experience = self.transform(buffer_xml, self.W_E_PATH)
        buffer_xml = self.get_string_representation(r_ed)
        html_education = self.transform(buffer_xml, self.ED_PATH)
        buffer_xml = self.get_string_representation(r_sk)
        html_computer_skills = self.transform(buffer_xml, self.SK_PATH)

        return html_learner_info, html_work_experience, html_education, \
            html_computer_skills

    def get_string(self, root, percent):
        language = ""
        el_learner_info = ""
        el_work_experience_list = ""
        el_education_list = ""
        el_computer_skills = ""
        for element in root.iter():
            if self.gettagns(element.tag)[1] == "SkillsPassport":
                language = element.attrib['locale']
            if self.gettagns(element.tag)[1] == "LearnerInfo":
                element.attrib['locale'] = language
                element.attrib['arg'] = percent
                el_learner_info = ET.tostring(element, pretty_print=True)
            if self.gettagns(element.tag)[1] == "WorkExperienceList":
                element.attrib['locale'] = language
                element.attrib['arg'] = percent
                el_work_experience_list = ET.tostring(element, \
                                                      pretty_print=True)
            if self.gettagns(element.tag)[1] == "EducationList" :
                element.attrib['locale'] = language
                element.attrib['arg'] = percent
                el_education_list = ET.tostring(element, pretty_print=True)
            if self.gettagns(element.tag)[1] == "Skills":
                element.attrib['locale'] = language
                element.attrib['arg'] = percent
                el_computer_skills = ET.tostring(element, pretty_print=True)

        if el_learner_info == "":
            el_learner_info = self.create_false_root("LearnerInfo",
                                                      language, percent)
        if el_work_experience_list == "":
            el_work_experience_list = \
            self.create_false_root("WorkExperienceList", language, percent)
        if el_education_list == "":
            el_education_list = \
                self.create_false_root("EducationList", language, percent)
        if el_computer_skills == "":
            el_computer_skills = \
                self.create_false_root("Skills", language, percent)
        return el_learner_info, el_work_experience_list, \
                el_education_list, el_computer_skills

    def create_false_root(self, label_root, language, percent):
        """
        # need to have a same root for all parts
        """
        root = ET.Element(label_root, locale=language, arg=percent)
        return ET.tostring(root, pretty_print=True)

    def gettagns(self, tag):
        """ returns a tuple of namespace,name """ 
        if tag[:1] == "{":
            return tag[1:].split("}", 1) 
        else:
            return (None, tag)

    def get_new_root_version(self):
        return ET.Element("version")

    def get_root_complete(self, array_node, root):
        cpt = 0
        while cpt < len(array_node):
            root.insert(cpt, ET.XML(array_node.__getitem__(cpt)))
            cpt += 1
        return root

    def get_string_representation(self, root):
        var = ET.tostringlist(root, pretty_print=True)
        buffer_xml = " "
        for val in var:
            buffer_xml += val
        return buffer_xml

    def transform(self, buffer_xml, path):
        flux = StringIO(buffer_xml)
        fileXSL = open(path, 'r')
        dataXSL = fileXSL.read()  
        xslt_root = ET.XML(dataXSL)
        transform = ET.XSLT(xslt_root)
        doc = ET.parse(flux)
        return transform(doc)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
