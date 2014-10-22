# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Cédric Pigeon
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _

PERIOD_ERROR_MSG = _('%s %s:'
                     ' period (from %s to %s) is not included in parent'
                     ' project period (from %s to %s)!')


def _check_dates(parent, child, child_name):
    parent_start = datetime.strptime(parent.date_start
                                     + ' 0000', '%Y-%m-%d %H%M')\
        if parent.date_start else False
    parent_stop = datetime.strptime(parent.date
                                    + ' 2359', '%Y-%m-%d %H%M')\
        if parent.date else False
    sub_start = datetime.strptime(child.date_start
                                  + ' 0000', '%Y-%m-%d %H%M')\
        if child.date_start else False
    sub_stop = datetime.strptime(child.date
                                 + ' 2359', '%Y-%m-%d %H%M')\
        if child.date else False

    if sub_start:
        if parent_start and sub_start < parent_start or \
           parent_stop and sub_start > parent_stop:
            raise exceptions.Warning(PERIOD_ERROR_MSG %
                                     (child_name,
                                      child.name if 'name' in child._columns
                                      else '',
                                      sub_start,
                                      sub_stop,
                                      parent_start,
                                      parent_stop))
    if sub_stop:
        if parent_start and sub_stop < parent_start or \
           parent_stop and sub_stop > parent_stop:
            raise exceptions.Warning(PERIOD_ERROR_MSG %
                                     (child_name,
                                      child.name if 'name' in child._columns
                                      else '',
                                      sub_start,
                                      sub_stop,
                                      parent_start,
                                      parent_stop))


class Project(models.Model):
    _inherit = 'project.project'

    parent_project_id = fields.Many2one('project.project',
                                        string='Parent project')
    subproject_ids = fields.One2many('project.project',
                                     'parent_project_id',
                                     string='Sub-Projects')
    subprojects_count = fields.Integer('Sub-project count',
                                       compute='_count_subprojects')

    @api.one
    @api.depends('subproject_ids')
    def _count_subprojects(self):
        self.subprojects_count = len(self.subproject_ids)

    @api.one
    @api.onchange('parent_project_id')
    def parent_project_id_change(self):
        if self.parent_project_id:
            self.parent_id = self.parent_project_id.analytic_account_id

    @api.one
    @api.constrains('date_start', 'date')
    def _check_date_consistency(self):
        """
            Check that sub-project period is included in parent project
            period
        """
        if self.parent_project_id:
            _check_dates(self.parent_project_id, self)

        if self.subproject_ids:
            for subproject in self.subproject_ids:
                _check_dates(self, subproject, _('Sub-Project'))

        if self.task_ids:
            for task in self.task_ids:
                _check_dates(self, task, _('Task'))

    @api.one
    @api.constrains('state')
    def _check_subprojects_state(self):
        if self.subproject_ids:
            for subproject in self.subproject_ids:
                if subproject.state != self.state:
                    raise exceptions.Warning(
                        _('Unable to update state of project while some'
                          ' subprojects are still in "%s" state !'
                          % self.state))


class Task (models.Model):
    _inherit = 'project.task'

    @api.one
    @api.constrains('date_start', 'date_end')
    def _check_date_consistency(self):
        if self.project_id:
            _check_dates(self.project_id, self, _('Task'))