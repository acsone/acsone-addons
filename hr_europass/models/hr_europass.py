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
import base64
from datetime import datetime
import logging
import os
import traceback

from openerp.addons.hr_europass.hr_europass_library.hr_europass_comparator\
    import master_update as master_update
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_pdf_extractor
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_report as objReport
from openerp.addons.hr_europass.hr_europass_library.hr_europass_parser\
    import hr_europass_xml as myParser

from openerp import api, fields, models
from openerp.exceptions import ValidationError, Warning
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


LANGUAGE = [
    ('en', 'English'),
    ('nl', 'Nederlands'),
    ('fr', 'French'),
]
CV_STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
]
EXTENTION = 'pdf'
EUROPASS_URL = 'europass.cedefop.europa.eu/editors/en/cv/compose'
_logger = logging.getLogger(__name__)


class HrEuropassCV(models.Model):

    _name = 'hr.europass.cv'
    _inherit = ['mail.thread']
    _inherits = {'mail.alias': 'mail_alias_id'}
    _description = 'HR Europass CV'

    @api.one
    @api.constrains('technical_name')
    def _check_unicity(self):
        """
        Check unicity on technical_name
        """
        domain = [
            ('technical_name', '=', self.technical_name),
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

    @api.model
    def _get_alias_vals(self):
        name = self._name
        vals = {
            'alias_model_name': name,
            'alias_parent_model_name': name,
        }
        return vals

    @api.one
    def _update_mail_alias(self):
        ir_cfg_obj = self.env['ir.config_parameter']
        catchall_alias = ir_cfg_obj.get_param('mail.catchall.alias')
        if not catchall_alias:
            raise (_('Please contact your Administrator '
                     'to configure a "catchall" email alias'))
        alias_name = '%s+%s+%s+%s' % (
            catchall_alias, self.first_name, self.last_name, self.id)
        alias_vals = {
            'alias_name': alias_name,
            'alias_parent_thread_id': self.id,
            'alias_force_thread_id': self.id,
        }
        self.mail_alias_id.write(alias_vals)

    @api.one
    @api.depends('draft_cv')
    def _compute_state(self):
        if self.draft_cv:
            self.state = 'draft'
        else:
            self.state = 'confirmed'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    technical_name = fields.Char(
        string='Technical Name', compute='_compute_technical_name', store=True)
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    fname = fields.Char(string='File Name')
    website = fields.Char(string='Europass', default=EUROPASS_URL)
    draft_fname = fields.Char(string='Draft fname')

    hr_employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee')
    hr_europass_consistency_id = fields.Many2one(
        comodel_name='hr.europass.consistency', string='Consistency',
        ondelete='cascade')
    mail_alias_id = fields.Many2one(
        comodel_name='mail.alias', required=True, ondelete='restrict',
        string='Email Alias')

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
        selection=CV_STATES, string='State', compute='_compute_state')

    # TODO: Use attachment to manage CV
    cv = fields.Binary(string='Europass CV', filters='*.pdf', required=True)
    draft_cv = fields.Binary(string='Draft CV', filters='*.pdf')

    last_update = fields.Datetime(string='Last update')

    @api.one
    def message_update(self, msg_dict, custom_values=None):
        """
        Update the CV value.
        **Warning**
        Only one CV by mail so one attachment by Email or first occurrence
        """
        attachments = msg_dict.get('attachments')
        if attachments:
            try:
                vals = {
                    'draft_cv': base64.encodestring(attachments[0][1]),
                    'draft_fname':  msg_dict['attachments'][0][0],
                }
                self.write(vals)
            except:
                _logger.error(_('A problem appears during the update '
                                'of %s' % self._name))

    @api.multi
    def compute_consistency(self):
        """
        """
        self.ensure_one()
        if not self.hr_europass_consistency_id:
            domain = [('name', '=', self.name)]
            consistency = self.hr_europass_consistency_id.search(domain)
            if not consistency:
                vals = {
                    'name': self.name,
                    'hr_europass_cv_ids': [[4, self.id]],
                }
                consistency = self.hr_europass_consistency_id.create(vals)
            else:
                self.hr_europass_consistency_id = consistency.id
        self.hr_europass_consistency_id._compute_consistency()

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
        content = self.cv.decode('base64')
        xml_right = hr_europass_pdf_extractor(content)._return_xml_from_pdf()

        # get xml from the draft version
        content = self.draft_cv.decode('base64')
        xml_draft = hr_europass_pdf_extractor(content)._return_xml_from_pdf()

        # send to library to get the html

        report_generator = master_update()
        report = report_generator.get_report_xml(xml_draft, xml_right)
        html = report_generator.get_html_from_xml(report)
        self.report_update = html

    @api.one
    def confirm_update(self):
        """
        Save the draft_cv into the cv and extract updated values
        for the model
        """
        vals = self._get_vals_from_xml(self.draft_cv)

        vals.update({
            'cv': self.draft_cv,
            'fname': self.draft_fname,
            'last_update': datetime.strftime(
                datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
            'draft_cv': False,
            'draft_fname': False,
            'report_update': False,
        })
        self.write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Receive a PDF from the binary field named 'cv'
        call the method '_get_vals_from_xml' to complete vals dictionary
        """
        if vals.get('fname'):
            ext = os.path.splitext(vals['fname'])
            if not len(ext) == 2 and ext[1] == EXTENTION:
                raise Warning(_('Error'), _('Only PDF are accepted'))
        vals.update(self._get_vals_from_xml(vals['cv']))
        if not vals.get('first_name') or not vals.get('last_name'):
            raise Warning(_('Error'), _("No name and/or last_name"))

        vals['last_update'] = datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        ctx = self.env.context.copy()
        ctx.update(
            self._get_alias_vals()
        )
        res = super(HrEuropassCV, self.with_context(ctx)).create(vals)
        res._update_mail_alias()
        return res

    @api.multi
    def unlink(self):
        search_name = list({cv.name for cv in self})
        res = super(HrEuropassCV, self).unlink()
        for name in search_name:
            domain = [('name', '=', name)]
            consistency = self.env['hr.europass.consistency'].search(domain)
            if consistency:
                if not len(consistency.hr_europass_cv_ids):
                    consistency.unlink()
                    continue
                consistency._compute_consistency()
        return res


class HrEuropassConsistency(models.Model):

    _name = 'hr.europass.consistency'
    _description = 'HR Europass Consistensty'

    def _chek_unicity(self):
        """
        Check unicity on [name]
        """
        domain = [
            ('name', '=', self.first_name),
        ]
        if len(self.search(domain)) > 1:
            raise ValidationError(
                _('Duplication is unauthorized (name)'))

    @api.one
    def _compute_consistency(self):
        request = []
        my_obj_report = objReport()
        for cv in self.hr_europass_cv_ids:
            if cv.state == 'confirm':
                content = cv.cv.decode('base64')
                xml = hr_europass_pdf_extractor(content)._return_xml_from_pdf()
                request.append(xml)
        if request:
            # This will return the fourth parts of the consistency
            l_i, w_e, ed, sk = my_obj_report.manage_list_cv(request)
            self.info_learner = l_i
            self.work_experiences = w_e
            self.skills = sk
            self.educations = ed

    name = fields.Char(string='Name')
    hr_europass_cv_ids = fields.One2many(
        comodel_name='hr.europass.cv',
        inverse_name='hr_europass_consistency_id', string='CVs')
    info_learner = fields.Text(string='Info Learner')
    work_experiences = fields.Text(string='Work Experiences')
    educations = fields.Text(string='Educations')
    skills = fields.Text(string='Skills')
