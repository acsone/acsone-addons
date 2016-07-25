# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import api, fields, models
from openerp.tools import SUPERUSER_ID
from openerp.addons.base_suspend_security.base_suspend_security import\
    BaseSuspendSecurityUid
from openerp.osv import expression
from openerp import tools


class ActivityRecordRule(models.Model):
    _inherit = 'ir.rule'
    _name = 'activity.record.rule'

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        return {'user': self.env.user,
                'time': time}

    @api.multi
    def _domain_force_get(self):
        eval_context = self._eval_context()
        for rule in self:
            if rule.domain_force:
                rule.domain = expression.normalize_domain(
                    eval(rule.domain_force, eval_context))
            else:
                rule.domain = []

    activity_id = fields.Many2one(comodel_name='workflow.activity',
                                  string='Activity',
                                  required=True)
    model_id = fields.Many2one(required=False, readonly=True)
    domain = fields.Binary(compute='_domain_force_get', string='Domain')

    @api.cr_uid
    def clear_cache(self, cr, uid):
        self._compute_activity_rule_domain.clear_cache(self)

    @api.multi
    def unlink(self):
        res = super(ActivityRecordRule, self).unlink()
        self.clear_cache()
        return res

    @api.model
    def create(self, vals):
        res = super(ActivityRecordRule, self).create(vals)
        self.clear_cache()
        return res

    @api.multi
    def write(self, vals):
        res = super(ActivityRecordRule, self).write(vals)
        self.clear_cache()
        return res

    @api.model
    def domain_get(self, model_name, activity_id):
        dom = self._call_compute_activity_rule_domain(activity_id)
        if dom:
            # _where_calc is called as superuser. This means that rules can
            # involve objects on which the real uid has no acces rights.
            # This means also there is no implicit restriction (e.g. an object
            # references another object the user can't see).
            query = self.env[model_name].sudo()._where_calc(dom,
                                                            active_test=False)
            return query.where_clause, query.where_clause_params, query.tables
        return [], [], ['"' + self.pool[model_name]._table + '"']

    @api.cr_uid
    def _call_compute_activity_rule_domain(self, cr, uid, activity_id):
        return self._compute_activity_rule_domain(cr, uid, activity_id)

    @tools.ormcache()
    @api.cr_uid
    def _compute_activity_rule_domain(self, cr, uid, activity_id):
        return self._local_compute_activity_rule_domain(cr, uid, activity_id)

    @api.model
    def _local_compute_activity_rule_domain(self, activity_id):
        if self._uid == SUPERUSER_ID or isinstance(self.env.uid,
                                                   BaseSuspendSecurityUid):
            return None
        self._cr.execute("""SELECT r.id
                FROM activity_record_rule r
                WHERE r.active is True
                AND r.activity_id = %s
                AND (r.id IN (SELECT rule_group_id FROM rule_group_rel g_rel
                JOIN res_groups_users_rel u_rel ON (g_rel.group_id = u_rel.gid)
                WHERE u_rel.uid = %s) OR r.global)""", (activity_id,
                                                        self._uid))
        rule_ids = [x[0] for x in self._cr.fetchall()]
        if rule_ids:
            # browse user as super-admin root to avoid access errors!
            user = self.env['res.users'].sudo().browse([self._uid])
            global_domains = []                 # list of domains
            group_domains = {}                  # map: group -> list of domains
            for rule in self.sudo().browse(rule_ids):
                # read 'domain' as UID to have the correct eval context for
                # the rule.
                rule_domain = rule.sudo(user=user.id)\
                    .read(['domain'])[0]['domain']
                dom = expression.normalize_domain(rule_domain)
                for group in rule.groups:
                    if group in user.groups_id:
                        group_domains.setdefault(group, []).append(dom)
                if not rule.groups:
                    global_domains.append(dom)
            # combine global domains and group domains
            if group_domains:
                group_domain = expression.OR(map(expression.OR,
                                                 group_domains.values()))
            else:
                group_domain = []
            domain = expression.AND(global_domains + [group_domain])
            return domain
        return []
