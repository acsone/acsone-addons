# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_europass, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_europass is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     hr_europass is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with hr_europass.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime
import logging
import os
import traceback

from openerp import api, fields, models

from openerp.addons.hr_europass.hr_europass_library.hr_europass_comparator\
    import master_update as master_update
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_pdf_extractor
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_report as objReport
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_xml as myParser

from openerp.exceptions import ValidationError, Warning
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


LANGUAGE = [
    ('en', 'English'),
    ('nl', 'Nederlands'),
    ('fr', 'French'),
]
CV_STATES = [
    ('new', 'New'),
    ('draft', 'Draft'),
    ('confirm', 'Confirmed'),
    ('refuse', 'Refused')
]
EXTENTION = 'pdf'
EUROPASS_URL = 'europass.cedefop.europa.eu/editors/en/cv/compose'
_logger = logging.getLogger(__name__)


class HrEuropassCV(models.Model):

    _name = 'hr.europass.cv'
    _description = 'HR Europass CV'

    @api.one
    @api.constrains('first_name', 'last_name', 'language')
    def _check_unicity(self):
        """
        Check unicity on [name, last_name, language]
        """
        domain = [
            ('first_name', '=', self.first_name),
            ('last_name', '=', self.last_name),
            ('language', '=', self.language)
        ]
        if len(self.search(domain)) > 1:
            raise ValidationError(
                _('Duplication is unauthorized (first_name, lastname, '
                  'language)'))

    @api.one
    @api.depends('last_name', 'first_name')
    def _compute_name(self):
        temp_name = ''
        if self.first_name or self.last_name:
            temp_name = '%s %s' % (self.first_name or '', self.last_name or '')
        self.name = temp_name

    @api.one
    @api.depends('last_name', 'first_name', 'language')
    def _compute_technical_name(self):
        self.technical_name =\
            '%s_%s_%s' % (self.first_name, self.last_name, self.language)

    @api.model
    def _get_vals_from_xml(self, cv):
        vals = {}
        try:
            content = cv.decode('base64')
            xml = hr_europass_pdf_extractor(content)._return_xml_from_pdf()
            myObjXml = myParser(xml)
            myObjXml._readXml(True)
            vals['first_name'] = myObjXml.first_name
            vals['last_name'] = myObjXml.last_name
            vals['language'] = myObjXml.language
            vals['raw_content'] = myObjXml.text
        except:
            traceback.print_exc()
            raise Warning(_("Invalid Europass PDF"))

        return vals

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    technical_name = fields.Char(
        string='Technical Name', compute='_compute_technical_name', store=True)
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    fname = fields.Char(string='File Name')
    website = fields.Char(string='Europass', default=EUROPASS_URL)
    draft_fname = fields.Char(string='Draft fname')

    attachment_id = fields.Many2one(comodel_name='ir.attachment', string='CV')
    hr_employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee')
    hr_europass_consistency_id = fields.Many2one(
        comodel_name='hr.europass.consistency', string='Consistency')

    info_learner = fields.Text(
        related='hr_europass_consistency_id.info_learner')
    work_experiences = fields.Text(
        related='hr_europass_consistency_id.work_experiences')
    educations = fields.Text(related='hr_europass_consistency_id.educations')
    skills = fields.Text(related='hr_europass_consistency_id.skills')
    note = fields.Text(string='Notes')
    raw_content = fields.Text(string='CV content')
    report_update = fields.Text(string='report update')

    language = fields.Selection(selection=LANGUAGE, string='Language')
    state = fields.Selection(
        selection=CV_STATES, string='State', default='new')

    cv = fields.Binary(string='Europass CV', filters='*.pdf', required=True)
    draft_cv = fields.Binary(string='Draft CV', filters='*.pdf')

    last_update = fields.Datetime(string='Last update')

    @api.multi
    def open_europass(self):
        """
        Open Europass Editor
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "https://europass.cedefop.europa.eu/editors/en/cv/compose",
            'target': 'current',
        }

    @api.one
    def update_request_report(self):
        """
        update the report_update field computed with the comparison of the
        current cv and the draft one
        """
        # get xml from the right version
        content = self.attachment_id.datas.decode('base64')
        xml_right = hr_europass_pdf_extractor(content)._return_xml_from_pdf()

        # get xml from the draft version
        content = self.draft_cv.decode('base64')
        xml_draft = hr_europass_pdf_extractor(content)._return_xml_from_pdf()

        # send to library to get the html

        report_generator = master_update()
        report = report_generator.get_report_xml(xml_draft, xml_right)
        html = report_generator.get_html_from_xml(report)
        self.report_update = html

    @api.multi
    def confirm(self):
        vals = {
            'state': 'confirm',
            'last_update': datetime.now()
        }
        res = super(HrEuropassCV, self).write(vals)
        return res

    @api.one
    def confirm_draft(self):
        """
        Save the draft_cv into the attachment_id and extract updated values
        for the model
        """
        vals = self._get_vals_from_xml(self.draft_cv)
        self.attachment_id.datas = self.draft_cv

        vals.update({
            'last_update': datetime.strftime(
                datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
            'draf_cv': False,
            'draf_fname': False,
        })
        self.write(vals)

    @api.one
    def refuse(self):
        """
        This method will reset the fields used into an update of CV
        And then restore the confirm state
        """
        vals = {
            'draft_cv': False,
            'draft_fname': False,
            'state': 'confirm',
            'report_update': False,
        }
        self.write(vals)

    @api.one
    def refuse_new(self):
        """
        Refuse a created CV
        """
        self.state = 'refuse'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Receive a PDF from the binary field named 'cv'
        call the method '_get_vals_from_xml' to complete vals dictionary
        """
        ext = os.path.splitext(vals['fname'])
        if not len(ext) == 2 and ext[1] == EXTENTION:
            raise Warning(_('Error'), _('Only PDF are accepted'))
        cv = vals.get('cv')
        if cv:
            vals.update(self._get_vals_from_xml(cv))
        if not vals.get('first_name') or not vals.get('last_name'):
            raise Warning(_('Error'), _("No name and/or last_name"))

        vals['last_update'] = datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        attachment_vals = {
            'name': vals['fname'],
            'datas': cv,
            'datas_fname': vals['fname'],
            'description': vals['note']
        }
        attach = self.attachment_id.create(attachment_vals)
        vals['attachment_id'] = attach.id
        res = super(HrEuropassCV, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        # TODO: Use a wizard to update CV and set cv readonly if set
        if vals.get('cv'):
            vals['draft_cv'] = vals.pop('cv')
            vals['draft_fname'] = vals.pop('fname')
        return super(HrEuropassCV, self).write(vals)


class HrEuropassConsistency(models.Model):

    _name = 'hr.europass.consistency'
    _description = 'HR Europass Consistensty'

    @api.one
    @api.depends('hr_europass_cv_ids.last_update')
    def _compute_consistency(self):
        request = []
        my_obj_report = objReport()
        for cv in self.hr_europass_cv_ids:
            content = cv.attachment_id.datas.decode('base64')
            xml = hr_europass_pdf_extractor(content)._return_xml_from_pdf()
            request.append(xml)
        if request:
            # This will return the fourth parts of the consistency
            l_i, w_e, ed, sk = my_obj_report.manage_list_cv(request)
            self.info_learner = l_i
            self.work_experiences = w_e
            self.skills = sk
            self.educations = ed

    @api.one
    @api.depends('hr_europass_cv_ids.name')
    def _compute_name(self):
        if self.hr_europass_cv_ids:
            self.name = self.hr_europass_cv_ids[0].name

    name = fields.Char(string='Name', compute='_compute_name')
    hr_europass_cv_ids = fields.One2many(
        comodel_name='hr.europass.cv',
        inverse_name='hr_europass_consistency_id', string='CVs',
        ondelete='cascade')
    info_learner = fields.Text(string='Info Learner')
    work_experiences = fields.Text(string='Work Experiences')
    educations = fields.Text(string='Educations')
    skills = fields.Text(string='Skills')


class HREuropassTrash(models.Model):

    _name = 'hr.europass.trash'
    _description = 'HR Europass Trash'

    file_name = fields.Char(string='File name')
    file = fields.Binary(string='File')
    write_date = fields.Datetime(string='Last update', readonly="True")
