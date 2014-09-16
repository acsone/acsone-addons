# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv import orm, fields


class wkf_transition(orm.Model):

    _inherit = 'workflow.transition'

    def action_launch(self, cr, uid, ids, context=None):
        '''
        Try to unblock a wkf instance launching the signal associated
        to a valid transition
        '''
        context = context or {}
        if context.get('active_instance_id'):
            signal = self.browse(cr, uid, ids, context=context)[0].signal
            inst_obj = self.pool['workflow.instance']
            inst = inst_obj.browse(cr, uid, context['active_instance_id'],
                                   context=context)
            obj_obj = self.pool[inst.res_type]
            cr.execute('SELECT create_uid, write_uid '
                       'FROM %s '
                       'WHERE id = %%s' % obj_obj._table,
                       (inst.res_id,))
            c_uid, w_uid = cr.fetchone()
            uid = w_uid or c_uid or uid
            obj_obj.signal_workflow(cr, uid, [inst.res_id], signal,
                                    context=context)
        return True


class wkf_instance(orm.Model):

    _inherit = 'workflow.instance'

    _columns = {
        'workitem_ids': fields.one2many('workflow.workitem', 'inst_id',
                                        string='Workitems'),
    }

    _order = 'res_type, res_id'

    def name_get(self, cr, uid, ids, context=None):
        ids = not ids and [] or isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.read(cr, uid, ids, ['res_type', 'res_id'],
                                context=context):
            display_name = '%s(%s)' % (record['res_type'], record['res_id'])
            res.append((record['id'], display_name))

        return res

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            if name.isdigit():
                args = ['|', ('res_type', operator, name),
                             ('res_id', '=', name)] + args
            else:
                args = [('res_type', operator, name)] + args
        ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def action_touch(self, cr, uid, ids, context=None):
        '''
        Try to unblock a wkf instance triggering a write access
        '''
        inst = self.browse(cr, uid, ids[0], context=context)
        obj_obj = self.pool[inst.res_type]
        cr.execute('SELECT create_uid, write_uid '
                   'FROM %s '
                   'WHERE id = %%s' % obj_obj._table,
                   (inst.res_id,))
        c_uid, w_uid = cr.fetchone()
        uid = w_uid or c_uid or uid
        obj_obj.step_workflow(cr, uid, [inst.res_id], context=context)
        return True


class wkf_workitem(orm.Model):

    _inherit = 'workflow.workitem'

    _columns = {
        'subwkf_id': fields.related('act_id', 'subflow_id',
                                    string='Sub Workflow',
                                    type='many2one', relation='workflow'),
        'out_trs_id': fields.related('act_id', 'out_transitions',
                                     string='Outgoing Transitions',
                                     type='one2many',
                                     relation='workflow.transition',),
    }

    def onchange_wkf_id(self, cr, uid, ids, wkf_id, inst_id, context=None):
        res = {
            'act_id': False,
        }
        if inst_id:
            instance_obj = self.pool['workflow.instance']
            inst = instance_obj.browse(cr, uid, inst_id, context=context)
            if inst.wkf_id.id != wkf_id:
                res.update({
                    'inst_id': False,
                })
        return {
            'value': res,
        }

    def onchange_act_id(self, cr, uid, ids, act_id, subwkf_id, context=None):
        res = {'subwkf_id': False}
        if act_id:
            activity_obj = self.pool['workflow.activity']
            act = activity_obj.browse(cr, uid, act_id, context=context)
            res.update({
                'subwkf_id': act.subflow_id.id,
            })
        if res['subwkf_id'] != subwkf_id:
            res.update({
                'subflow_id': False,
            })
        return {
            'value': res,
        }
