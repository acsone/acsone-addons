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
from openerp.addons.base_suspend_security.base_suspend_security import\
    BaseSuspendSecurityUid


class WorkflowActivityAction(models.Model):
    _name = 'workflow.activity.action'

    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity',
                                  required=True, ondelete='cascade')
    name = fields.Char(required=True, translate=True)
    action = fields.Many2one(comodel_name='ir.actions.server', required=True)

    @api.multi
    def do_action(self):
        self.ensure_one()
        res_id = self.env.context.get('res_id', False)
        res_type = self.env.context.get('res_type', False)
        assert res_id and res_type
        self.activity_id.check_action_security(res_type, res_id)
        self = self.suspend_security()
        ctx = dict(self.env.context,
                   active_model=res_type, active_ids=[res_id],
                   active_id=res_id)
        res = self.action.with_context(ctx).run()
        return res


class WorkflowActivity(models.Model):
    _inherit = 'workflow.activity'

    use_action_object = fields.Boolean(
        string="Show actions on object",
        help="""Si vrai et si les conditions de sécurité sont satisfaites,\
                les actions peuvent être utilisés directement sur l'objet""")
    action_ids = fields.One2many(comodel_name='workflow.activity.action',
                                 inverse_name='activity_id',
                                 string='Actions',
                                 help="Actions that can be triggered with "
                                      "buttons on the task form. This is "
                                      "useful when the activity cannot be "
                                      "completed through normal actions "
                                      "on the underlying object.")
    security_group_ids = fields.Many2many(
        comodel_name='res.groups', relation='activity_groups_rel',
        column1='activity_id', column2='group_id', string='Security Groups',
        help="""Groupes de sécurité pouvant intéragir avec un objet dans\
                cette activité que ce soit au niveau de la visibilité des\
                tâches ou des actions""")
    activity_rule_ids = fields.One2many(
        comodel_name='activity.record.rule', inverse_name='activity_id',
        string="Activity Record Rule",
        help="""Règles de sécurité devant être satisfaites pour l'affichage\
                et l'utilisation des actions""")

    @api.multi
    def check_action_security(self, res_type, res_id):
        if not self._check_action_security(res_type, res_id):
            raise exceptions.AccessError(
                _("""The requested operation cannot be completed due to
                     security restrictions.
                     Please contact your system administrator."""))

    @api.multi
    def _check_action_security(self, res_type, res_id):
        self.ensure_one()
        if self._uid == SUPERUSER_ID or\
                isinstance(self.env.uid, BaseSuspendSecurityUid):
            return True
        if self.security_group_ids.ids:
            act = self.search(
                [('security_group_ids.users', '=', self.env.user.id),
                 ('id', '=', self.id)])
            if not act.ids:
                return False
        obj = self.env[res_type].browse([res_id])
        table = obj._table
        res = False
        if obj.is_transient():
            self._cr.execute("""SELECT distinct create_uid
                                FROM %s
                                WHERE id IN %%s""" % (obj._table,
                                                      (tuple(obj._ids),)))
            uids = [x[0] for x in self._cr.fetchall()]
            if len(uids) != 1 or uids[0] != SUPERUSER_ID or\
                    not isinstance(self.env.uid, BaseSuspendSecurityUid):
                res = False
        else:
            where_clause, where_params, tables =\
                self.env['activity.record.rule'].domain_get(res_type, self.id)
            if where_clause:
                where_clause = ' and ' + ' and '.join(where_clause)
                sub_ids = (obj.id,)
                self._cr.execute(
                    'SELECT ' + table + '.id FROM ' + ','.join(tables) +
                    ' WHERE ' + table + '.id IN %s' + where_clause,
                    [sub_ids] + where_params)
                returned_ids = [x['id'] for x in self._cr.dictfetchall()]
                res = self._check_record_rules_result_count(table, sub_ids,
                                                            returned_ids)
            else:
                res = True
        return res

    @api.model
    def _check_record_rules_result_count(self, res_type, sub_res_ids,
                                         result_ids):
        ids, result_ids = set(sub_res_ids), set(result_ids)
        missing_ids = ids - result_ids
        if missing_ids:
            self._cr.execute(
                'SELECT id FROM ' + res_type + ' WHERE id IN %s',
                (tuple(missing_ids),))
            forbidden_ids = [x[0] for x in self._cr.fetchall()]
            if forbidden_ids:
                if self._uid == SUPERUSER_ID or\
                        isinstance(self.env.uid, BaseSuspendSecurityUid):
                    return True
                return False
            else:
                return True
        return True
