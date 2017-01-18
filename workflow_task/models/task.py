# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of workflow_task,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     workflow_task is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     workflow_task is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with workflow_task.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.tools import SUPERUSER_ID
import itertools


class Task(models.Model):
    _name = 'workflow.task'
    _inherit = ['mail.thread']
    _description = "Workflow Task"

    @api.model
    def _select_objects(self):
        model_obj = self.env['ir.model']
        models = model_obj.search([])
        return [(r.model, r.name) for r in models] + [('', '')]

    name = fields.Char(related='activity_id.name')
    workitem = fields.Many2one(comodel_name='workflow.workitem')
    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity', required=True)
    description = fields.Text()
    user_id = fields.Many2one(comodel_name='res.users',
                              string='Assigned User',
                              track_visibility='onchange')
    state = fields.Selection([('new', 'Todo'),
                              ('started', 'In progress'),
                              ('closed', 'Closed')], default='new',
                             track_visibility='onchange')
    date_deadline = fields.Date(string="Deadline",
                                track_visibility='onchange')
    date_critical = fields.Date(
        help="""The created task will appear in red in the task tree view
            after this date""")
    date_started = fields.Datetime(string="Started on",
                                   track_visibility='onchange')
    date_closed = fields.Datetime(string="Closed on",
                                  track_visibility='onchange')
    res_type = fields.Selection(selection=_select_objects, string='Type',
                                required=True)
    res_id = fields.Integer(string='ID', required=True)
    ref_object = fields.Reference(string='Objet',
                                  selection=_select_objects,
                                  store=True, compute='_get_ref_object')
    ref_object_name = fields.Char(search='_search_ref_object',
                                  compute='_dummy_compute',
                                  string="Related object")
    action_ids = fields.One2many(comodel_name='workflow.activity.action',
                                 compute='_get_action_ids')
    pretty_res_type = fields.Char(compute='_get_pretty_res_type')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(Task, self).fields_get(allfields, attributes)
        # remove ref_object from searchable field into the advanced search
        # since the field to use is ref_object_name
        if 'ref_object' in res:
            res['ref_object']['searchable'] = False
        return res

    @api.multi
    @api.depends('res_type')
    def _get_pretty_res_type(self):
        for record in self:
            model = self.env['ir.model']\
                .search([('model', '=', record.res_type)])
            record.pretty_res_type = model.name

    def _search_ref_object(self, operator, value):
        self._cr.execute("""SELECT distinct res_type FROM workflow_task""")
        models = self._cr.fetchall()
        all_task_ids = []
        for model in models:
            model = model[0]
            self._cr.execute("""SELECT distinct res_id FROM workflow_task
                WHERE res_type=%s""", (model,))
            mids = [r[0] for r in self._cr.fetchall()]
            if not self.env[model].check_access_rights(
                    'read',  raise_exception=False):
                continue
            ns_result = self.env[model].name_search(
                name=value, operator=operator, args=[('id', 'in', mids)])
            obj_ids = [r[0] for r in ns_result]
            tids = self.search([('res_type', '=', model),
                                ('res_id', 'in', obj_ids)])
            all_task_ids.extend(tids._ids)
        return [('id', 'in', all_task_ids)]

    @api.depends('ref_object')
    @api.multi
    def _dummy_compute(self):
        for record in self:
            record.ref_object_name = record.ref_object

    @api.multi
    def _get_action_ids(self):
        for record in self:
            if record.activity_id.use_action_task and\
                    record.activity_id._check_action_security(record.res_type,
                                                              record.res_id):
                record.action_ids = record.activity_id.action_ids

    @api.multi
    def start_task(self):
        for record in self:
            record.date_started = fields.Datetime.now()
            record.state = 'started'
            record.user_id = self.env.uid

    @api.multi
    def close_task(self):
        for record in self:
            record.date_closed = fields.Datetime.now()
            record.state = 'closed'
            record.user_id = False

    @api.depends('res_type', 'res_id')
    @api.one
    def _get_ref_object(self):
        if self.res_type and self.res_id:
            self.ref_object = '%s,%s' % (self.res_type, str(self.res_id))

    @api.multi
    def _check_activity_security(self):
        self._cr.execute(
            """SELECT id, res_type, res_id, activity_id FROM workflow_task
               WHERE id = ANY(%s)""", (list(self._ids),))
        targets = self._cr.dictfetchall()
        res = {}
        for task_dict in targets:
            if not self.pool['workflow.activity'].\
                    _check_action_security(self._cr, self._uid,
                                           [task_dict['activity_id']],
                                           task_dict['res_type'],
                                           task_dict['res_id']):
                res[task_dict['id']] = False
            else:
                res[task_dict['id']] = True
        return res

    @api.multi
    def check(self, mode, values=None):
        """Restricts the access to a workflow task, according to
           referred model.
        """
        res_ids = {}
        if self._ids:
            self._cr.execute(
                """SELECT DISTINCT res_type, res_id FROM
                   workflow_task WHERE id = ANY (%s)""", (list(self._ids),))
            for rmod, rid in self._cr.fetchall():
                res_ids.setdefault(rmod, set()).add(rid)
        if values:
            if values.get('res_type') and values.get('res_id'):
                res_ids.setdefault(values['res_type'], set())\
                    .add(values['res_id'])

        for model, mids in res_ids.items():
            existing_ids = self.env[model].browse(mids).exists()
            existing_ids.check_access_rule(mode)
        if not self._uid == SUPERUSER_ID and\
                not self.env['res.users'].has_group('base.group_user'):
            raise exceptions.AccessError(
                _("Sorry, you are not allowed to access this document."))

    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        ids = super(Task, self)._search(args, offset=0,
                                        limit=None, order=order,
                                        count=False,
                                        access_rights_uid=access_rights_uid)
        if not ids:
            if count:
                return 0
            return []
        orig_ids = ids
        ids = set(ids)
        self.env.cr.execute(
            """SELECT id, res_type, res_id FROM workflow_task
               WHERE id = ANY(%s)""", (list(ids),))
        targets = self.env.cr.dictfetchall()
        model_tasks = {}
        for target_dict in targets:
            if not target_dict['res_type']:
                continue
            # model_tasks = { 'model': { 'res_id': [id1,id2] } }
            model_tasks.setdefault(target_dict['res_type'], {})\
                .setdefault(target_dict['res_id'] or 0, set())\
                .add(target_dict['id'])

        # To avoid multiple queries for each task found, checks are
        # performed in batch as much as possible.
        ima = self.env['ir.model.access']
        for model, targets in model_tasks.iteritems():
            if model not in self.env:
                continue
            if not ima.check(model, 'read', False):
                # remove all corresponding task ids
                for attach_id in itertools.chain(*targets.values()):
                    ids.remove(attach_id)
                continue  # skip ir.rule processing,these ones are out already

            # filter ids according to what access rules permit
            target_ids = targets.keys()
            allowed_ids = [0] + self.env[model].search(
                [('id', 'in', target_ids)]).ids
            disallowed_ids = set(target_ids).difference(allowed_ids)
            for res_id in disallowed_ids:
                for attach_id in targets[res_id]:
                    ids.remove(attach_id)
#         activity_security = self._check_activity_security(cr, uid, ids,
#                                                           context=context)
#         for task_id, res in activity_security.iteritems():
#             if not res:
#                 ids.remove(task_id)
        # sort result according to the original sort ordering
        result = [id for id in orig_ids if id in ids]
        ids = super(Task, self)._search( [('id', 'in', result)],
                                        offset=offset, limit=limit,
                                        order=order, count=False,
                                        access_rights_uid=access_rights_uid)
        return len(ids) if count else list(ids)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        self.check('read')
        return super(Task, self).read(fields=fields, load=load)

    @api.multi
    def write(self, vals):
        # If mode is write, it's impossible to start the task
        self.check('read', values=vals)
        return super(Task, self).write(vals)

    @api.multi
    def copy(self, default=None):
        self.check('write')
        return super(Task, self).copy(default=default)

    @api.multi
    def unlink(self):
        self.check('unlink')
        return super(Task, self).unlink()

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        self.check('write', values=values)
        return super(Task, self).create(values)
