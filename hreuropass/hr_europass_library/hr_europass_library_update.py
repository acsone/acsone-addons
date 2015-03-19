# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Jonathan Nemry & USER
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
import os

"""
# Constant
"""
NAME_SPACE = "{http://europass.cedefop.europa.eu/Europass}"
LEARNER = "LearnerInfo"
SKILLS = "Skills"
COMPUTER = "Computer"
DESCRIPTION = "Description"
IDENTIFICATION = "Identification"
PERSON_NAME = "PersonName"
FIRST_NAME = "FirstName"
SURNAME = "Surname"
POSITION = "Position"
ACTIVITIES = "Activities"
TITLE = "Title"
LABEL = "Label"

PATH_STYLE_ROOT = os.path.dirname(__file__) + "/../static/src/style/"

class  hr_europass_element_update():

    """
    # hr_europass_element_update
    # using like a container of the data to conserve all informations of the 
    # update request 
    """
    
    def __init__(self, label):
        self.label = label
        self.array_new = []
        self.array_delete = []
        self.array_modify = []
        self.array_warnings = []
    """
    # method to add text depending the type (del-new-modify-warnings)
    """
    def add_new(self, text):
        self.array_new.append(text)
    def add_delete(self, text):
        self.array_delete.append(text)
    def add_modify(self, text):
        self.array_modify.append(text)
    def add_warnings(self, text):
        self.array_warnings.append(text)
    def has_nothing(self):
        if not self.array_delete and \
            not self.array_modify and \
            not self.array_new and \
            not self.array_warnings:
            self.add_warnings("Nothing has changed")
    def to_string(self):
        """
        # to string methode, only used to made test, very helpfull if you
        # have bug in the treatment of the data
        """
        buffer = "\n" + self.label
        if len(self.array_new) is not 0:
            buffer += "\nNew:"
        for new in self.array_new:
            buffer += "\n" + new
            
        if len(self.array_delete) is not 0:
            buffer += "\nDelete:"
        for delete in self.array_delete:
            buffer += "\n" + delete
            
        if len(self.array_modify) is not 0:
            buffer += "\nModify:"
        for modify in self.array_modify:
            buffer += "\n" + modify
        if self.label != "User info" and self.label != "Computer skills":
            if len(self.array_warnings) is not 0:
                buffer += "\nWarnings:"
            for warning in self.array_warnings:
                buffer += "\n" + warning
        
        return buffer


class hr_europass_matching_update():


    """
    # hr_europass_matching_update
    # provide methods to get comparison between some parts of the CV
    # it always like this: and old and a new version. of the SAME CV
    """

    
    def gettagns(self, tag):
        """
        # get tag ns return tab of namespace and name tag
        # if no namespace, return None to the pos 0 of the tab
        # it's use to have the possibility to make a comparison of the 
        # tag name without the namespace 
        """ 
        if tag[:1] == "{":
            return tag[1:].split("}", 1) 
        else:
            return (None, tag)
    
    def get_computer_skills(self, root):
        """
        # racine of a CV, try to find skills, if found, then return true
        # and the content of the skills
        # else return false
        """
        find = False
        skills_computer_text = " "
        learner_info = root.find(NAME_SPACE + LEARNER)
        if learner_info is not None:
            skills_new = learner_info.find(NAME_SPACE + SKILLS)
            if skills_new is not None:
                computer = skills_new.find(NAME_SPACE + COMPUTER)
                if computer is not None:
                    description = computer.find(NAME_SPACE + DESCRIPTION)
                    if description is not None:
                        skills_computer_text = description.text
                        find = True
        return find, skills_computer_text

    def count_number_w_e_and_ed(self, root):
        
        """
        # root of the CV
        # this method ll count the number of education and workexperience of
        # the CV
        # return number of each elements and the element themselves
        # if nothing found for one or the other, then return 0 and None for
        # the element
        """
        cpt_w_e = 0
        cpt_ed = 0
        w_e_l = None
        ed_l = None
        for el_old in root.iter():  
            if self.gettagns(el_old.tag)[1] == "EducationList": 
                ed_l = el_old 
            if self.gettagns(el_old.tag)[1] == "WorkExperienceList": 
                w_e_l = el_old 
            if self.gettagns(el_old.tag)[1] == "WorkExperience":
                cpt_w_e += 1
            if self.gettagns(el_old.tag)[1] == "Education":
                cpt_ed += 1
        return cpt_w_e, cpt_ed, w_e_l, ed_l

    def compare_computer_skills(self, find_new, find_old,
                                 text_new, text_old, report):

        """
        # this method ll write into report if the skills are modified, deleted
        # of added, if nothing changed, then nothin ll write
        """
        if not find_new and find_old:
            report.add_delete("Computer skills have been deleted")
        elif find_new and not find_old:
            report.add_new("Computer skills have been added")
        elif find_new and find_old:
            text_new = text_new.replace(" ", "")
            text_old = text_old.replace(" ", "")
            if text_new != text_old:
                report.add_modify("Computer skills have been changed")
        return report

    def get_learner_info(self, root):
        """
        # get_learner_info
        # from root, return information of the learner.
        # here, it's simply the last name and the surname
        #
        """
        find_name = False
        find_surname = False
        first_name_text = ""
        surname_text = ""
        result = []
        learner_info = root.find(NAME_SPACE + LEARNER)
        if learner_info is not None:
            identification = learner_info.find(NAME_SPACE + IDENTIFICATION)
            if identification is not None:
                person_name = identification.find(NAME_SPACE + PERSON_NAME)
                if person_name is not None:
                    first_name = person_name.find(NAME_SPACE + FIRST_NAME)
                    if first_name is not None:
                        first_name_text = first_name.text
                        find_name = True
                    surname = person_name.find(NAME_SPACE + SURNAME)
                    if surname is not None:
                        surname_text = surname.text
                        find_surname = True
        result.append(find_name)
        result.append(find_surname)
        result.append(first_name_text)
        result.append(surname_text)
        return result

    def compare_learner_info(self, result_new, result_old, report):
        """
        # to compare the name and the other name,
        # to compare the surname and the other surname
        # to compare if name has been added/delete
        # to write into the report the modification that has been found
        """
        find_name_new = result_new.__getitem__(0)
        find_name_old = result_old.__getitem__(0)
        name_new = result_new.__getitem__(2)
        name_old = result_old.__getitem__(2)
        name_new = name_new.replace(" ", "")
        name_old = name_old.replace(" ", "")
        report = self.compare_element(find_name_new, find_name_old,
                                      name_new, name_old, "Name", report)
        find_surname_new = result_new.__getitem__(1)
        find_surname_old = result_old.__getitem__(1)
        surname_new = result_new.__getitem__(3)
        surname_old = result_old.__getitem__(3)
        surname_new = surname_new.replace(" ", "")
        surname_old = surname_old.replace(" ", "")
        report = self.compare_element(find_surname_new, find_surname_old,
                                       surname_new, surname_old, "Surname",
                                        report)
        return report
    
    def compare_element(self , find_new, find_old, text_new,
                         text_old, var_text, report):
        """
        # receive an element of two different sources
        # compare the two
        # if the boolean of the elements are not same, write the corresponding
        # sense of this difference into the report
        """
        if not find_new and find_old:
            report.add_delete(var_text + " have been deleted")
        elif find_new and not find_old:
            report.add_new(var_text + " have been added")
        elif find_new and find_old:            
            if text_new != text_old:
                report.add_modify(var_text + " have changed")

        return report

    def compare_w_e_old_with_new(self, root_old, root_new, report):
        """
        # get a old_root and a new root.
        # this will compare every work experience one with each other
        # and get conclusion of this
        # write into report if new/modify/deleted and warning if all has been
        # added or deleted
        """
        cpt_old = 0
        end_root_new = root_new
        find_old = False
        for el_old in root_old.iter():
            if self.gettagns(el_old.tag)[1] == "WorkExperience":
                cpt_new = 0
                for el_new in root_new.iter():
                    if self.gettagns(el_new.tag)[1] == "WorkExperience":
                        find_old = False
                        report, continue_loop = self.compare_two_w_e(el_new,
                                                                    cpt_new,
                                                                    el_old,
                                                                    cpt_old,
                                                                    report)
                        if not continue_loop:     
                            el_new.getparent().remove(el_new)
                            end_root_new = root_new 
                            find_old = True
                            break
                    cpt_new += 1
                if find_old is False:
                    report = self.get_title_we_del(report, el_old)
            cpt_old += 1
        for el_new in end_root_new.iter():
            if self.gettagns(el_new.tag)[1] == "WorkExperience":
                position = el_new.find(NAME_SPACE + POSITION)
                if position is not None:
                    label_new = position.find(NAME_SPACE + LABEL)
                    report.add_new(label_new.text)
        return report

    def compare_two_w_e(self, ed_new, place_new, ed_old, place_old, report):
        """
        # get a old_root and a new root.
        # this will compare every educations one with each other
        # and get conclusion of this
        # write into report if new/modify/deleted and warning if all has been
        # added or deleted
        """
        find_pos_new = False
        find_pos_old = False
        continue_loop = True
        title_new = None
        position_new = ed_new.find(NAME_SPACE + POSITION)   
        if position_new is not None:
            label_new = position_new.find(NAME_SPACE + LABEL)
            title_new = label_new.text
            find_pos_new = True

        position_old = ed_old.find(NAME_SPACE + POSITION)

        if position_old is not None:
            label_old = position_old.find(NAME_SPACE + LABEL)
            title_old = label_old.text
            find_pos_old = True

        if find_pos_old and find_pos_new:
            if title_old == title_new:
                continue_loop = False
                has_text_new = False
                has_text_old = False
                activity_new = ed_new.find(NAME_SPACE + ACTIVITIES)
                if activity_new is not None:
                    content_new = activity_new.text
                    has_text_new = True

                activity_old = ed_old.find(NAME_SPACE + ACTIVITIES)
                if activity_old is not None:
                    content_old = activity_old.text
                    has_text_old = True

                if has_text_old and has_text_new:
                    content_new = content_new.replace(" ", "")
                    content_old = content_old.replace(" ", "")
                    if content_new != content_old:
                        report.add_modify(title_new)

                elif has_text_old and not has_text_new:
                    report.add_warnings(title_new + """" activity has been 
                                                    deleted""")
                elif has_text_new and not has_text_old:
                    report.add_warnings(title_new + "activity has been added")

        return report, continue_loop

    def get_title_ed_del(self, report, element):
        """
        # return the report of and education
        # with the title wrote into delete field of the report
        """
        position_new = element.find(NAME_SPACE + TITLE)   
        if position_new is not None:
            report.add_delete(position_new.text)
        return report

    def compare_ed_old_with_new(self, root_old, root_new, report):   
        """
        # write into report the differences found into the root_old and the 
        # root_new
        """
        cpt_old = 0
        end_root_new = root_new
        find_old = False
        for el_old in root_old.iter():
            if self.gettagns(el_old.tag)[1] == "Education":
                cpt_new = 0
                for el_new in root_new.iter():
                    if self.gettagns(el_new.tag)[1] == "Education":
                        find_old = False
                        report, continue_loop = self.compare_two_ed(el_new,
                                                                    cpt_new,
                                                                    el_old,
                                                                    cpt_old,
                                                                    report)
                        if not continue_loop:
                            # that means we have find matching label
                            el_new.getparent().remove(el_new)
                            end_root_new = root_new
                            find_old = True
                            break
                    cpt_new += 1
            cpt_old += 1
            if find_old is False:
                    report = self.get_title_ed_del(report, el_old)
        for el_new in end_root_new.iter():
            if self.gettagns(el_new.tag)[1] == "Education":
                position = el_new.find(NAME_SPACE + TITLE)
                if position is not None:
                    report.add_new(position.text)
        return report

    def get_title_we_del(self, report, element):
        """
        # write the title of element into the report and return it
        """
        position_new = element.find(NAME_SPACE + POSITION)   
        if position_new is not None:
            label_new = position_new.find(NAME_SPACE + LABEL)
            report.add_delete(label_new.text)
        return report

    def compare_two_ed(self, ed_new, place_new, ed_old, place_old, report):
        """
        # two educations 
        # same that the others : check difference and write into report
        """
        find_pos_new = False
        find_pos_old = False
        continue_loop = True
        title_new = None
        position_new = ed_new.find(NAME_SPACE + TITLE)
        if position_new is not None:
            title_new = position_new.text
            find_pos_new = True

        position_old = ed_old.find(NAME_SPACE + TITLE)

        if position_old is not None:
            title_old = position_old.text
            find_pos_old = True

        if find_pos_old and find_pos_new:
            if title_old == title_new:
                continue_loop = False
                has_text_new = False
                has_text_old = False
                activity_new = ed_new.find(NAME_SPACE + ACTIVITIES)
                if activity_new is not None:
                    content_new = activity_new.text
                    has_text_new = True

                activity_old = ed_old.find(NAME_SPACE + ACTIVITIES)
                if activity_old is not None:
                    content_old = activity_old.text
                    has_text_old = True

                if has_text_old and has_text_new:
                    content_new = content_new.replace(" ", "")
                    content_old = content_old.replace(" ", "")
                    if content_new != content_old:
                        report.add_modify(title_new)
                    
                elif has_text_old and not has_text_new:
                    report.add_warnings(title_new + """
                            activity has been deleted""")
                elif has_text_new and not has_text_old:
                    report.add_warnings(title_new + """
                            activity has been added""")

        return report, continue_loop


class master_update():
    """
    # master update is a class used by the module, to simplified the 
    # comparison because it's too long for write it into the model cv
    """

    def get_report_xml(self, root_new, root_old):

        """
        # principal method:
        # just need to call it to have the xml output
        """
        my_matcher = hr_europass_matching_update()
        my_element_skills = hr_europass_element_update("Computer skills")
        my_element_info = hr_europass_element_update("User info")
        my_element_exp = hr_europass_element_update("Work experience")
        my_element_ed = hr_europass_element_update("Education")
        
        """ next step is parsing the data one to one to find 
            the number of item of Work experience and formation
        """
        root_new = ET.XML(root_new)
        root_old = ET.XML(root_old)
        cpt_w_e_new, cpt_ed_new, w_e_l_new, ed_l_new = \
            my_matcher.count_number_w_e_and_ed(root_new)
        cpt_w_e_old, cpt_ed_old, w_e_l_old, ed_l_old = \
            my_matcher.count_number_w_e_and_ed(root_old)


        if cpt_w_e_new == 0 and cpt_w_e_old != 0:
            my_element_exp.add_warnings("All experiences have been deleted")
        if cpt_w_e_new != 0 and cpt_w_e_old == 0:
            my_element_exp.add_warnings("First adding of experiences")
        if cpt_ed_new == 0 and cpt_ed_old != 0:
            my_element_exp.add_warnings("All educations have been deleted")
        if cpt_ed_new != 0 and cpt_ed_old == 0:
            my_element_exp.add_warnings("First adding of educations")

        """
        # first compare the learner info and the skills
        """
        find_new, text_new = my_matcher.get_computer_skills(root_new)
        find_old, text_old = my_matcher.get_computer_skills(root_old)
        
        my_element_skills = my_matcher.compare_computer_skills(find_new,
                                                               find_old,
                                                               text_new,
                                                               text_old,
                                                            my_element_skills)
        """
        # learner info
        """
        result_new = my_matcher.get_learner_info(root_new)
        result_old = my_matcher.get_learner_info(root_old)
        my_element_info = my_matcher.compare_learner_info(result_new,
                                                        result_old,
                                                        my_element_info)
        if root_old.attrib['locale'] != root_new.attrib['locale']:
            my_element_info.add_modify("Language")
        """
            Work experience
        """
        if w_e_l_old is not None and w_e_l_new is not None:
            my_element_exp = my_matcher.compare_w_e_old_with_new(w_e_l_old,
                                                            w_e_l_new,
                                                            my_element_exp)

        """
            Education
        """
        if ed_l_old is not None and ed_l_new is not None:
            my_element_ed = my_matcher.compare_ed_old_with_new(ed_l_old,
                                                               ed_l_new,
                                                               my_element_ed)
        """
        # Make an array with all the parts
        """
        array_element = []
        my_element_info.has_nothing()
        my_element_skills.has_nothing()
        my_element_exp.has_nothing()
        my_element_ed.has_nothing()
        array_element.append(my_element_info)
        array_element.append(my_element_exp)
        array_element.append(my_element_ed)        
        array_element.append(my_element_skills)

        xml_output = self.create_xml_output(array_element)
        return xml_output

    def create_xml_output(self, array_element):
        """
        # create and new xml from all the parts of type reports
        """
        root = ET.Element("root")
        cpt = 0
        for element in array_element:
            xml_tree = self.create_element(element)
            root.insert(cpt, xml_tree)
            cpt += 1
        return root

    def create_element(self, element_obj):
        """
        # inspect the array of the element and create a new architecture
        # for element into xml
        """
        root = ET.Element("element")
        root.insert(0, ET.Element("type"))
        root[0].text = element_obj.label
        cpt = 0
        if len(element_obj.array_new) != 0:
            xml_new = self.get_list(element_obj.array_new, "added")
            root.insert(cpt, xml_new)
            cpt += 1
        if len(element_obj.array_delete) != 0:
            xml_delete = self.get_list(element_obj.array_delete, "deleted")
            root.insert(cpt, xml_delete)
            cpt += 1
        if len(element_obj.array_modify) != 0:
            xml_modify = self.get_list(element_obj.array_modify, "modified")
            root.insert(cpt, xml_modify)
            cpt += 1

        if len(element_obj.array_warnings) != 0:
            if "Nothing has changed" in element_obj.array_warnings[0]:
                xml_warnings = self.get_list(element_obj.array_warnings,
                                         "Note:")
            else:
                xml_warnings = self.get_list(element_obj.array_warnings,
                                         "warnings:")
            root.insert(cpt, xml_warnings)
        return root

    def get_list(self, array, type_spec):
        """
        # return the list xml of the array content
        """
        root = ET.Element("list", name=type_spec)
        cpt = 0
        for content in array:
            root.insert(cpt, ET.Element("field"))
            root[cpt].text = content
            cpt += 1
        return root

    def get_html_from_xml(self, xml):
        """
        # return html from xml
        # with the style sheet
        """
        fileXSL = open(PATH_STYLE_ROOT + 'style_report.xsl', 'r')
        dataXSL = fileXSL.read()

        xslt_root = ET.XML(dataXSL)
        transform = ET.XSLT(xslt_root)
        dataXML = ET.tostring(xml)
        flux = StringIO(dataXML)
        doc = ET.parse(flux)
        result_tree = transform(doc)  

        return result_tree 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

