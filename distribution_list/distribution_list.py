# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class distribution_list(orm.Model):

    _name = 'distribution.list'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID'),
        'name': fields.char(string='Name', required=True, track_visibility='onchange'),
        'to_include_distribution_list_line_ids': fields.many2many('distribution.list.line',
                                              'include_distribution_list_line_rel',
                                              'include_distribution_list_id',
                                              'include_distribution_list_line_id', string="Filter To Include"),
        'to_exclude_distribution_list_line_ids': fields.many2many('distribution.list.line',
                                              'exclude_distribution_list_line_rel',
                                              'exclude_distribution_list_id',
                                              'exclude_distribution_list_line_id', string="Filter To Exclude"),
        'company_id': fields.many2one('res.company', 'Company'),
        'dst_model_id': fields.many2one('ir.model', 'Destination Model', required=True),
        'bridge_field': fields.char('Bridge Field', required=True,
                                    help="A common field name that make bridge between\
                                          source model of filters and target model of  distribution list"),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(cr, uid,
                                                          'distribution.list', context=c),
        'dst_model_id': lambda self, cr, uid, c:
        self.pool.get('ir.model').search(cr, uid, [('model', '=', 'res.partner')], context=c)[0],
        'bridge_field': 'id',
    }
    _sql_constraints = [('unique_name_by_company', 'unique(name,company_id)', 'Name Must Be Unique By Company')]

    def mass_mailing(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        dist_list = self.browse(cr, uid, ids, context=context)[0]
        ir_model_data = self.pool.get('ir.model.data')
        ref_template = ir_model_data.get_object_reference(cr, uid, 'distribution_list', 'email_template_partner_distribution_list')[1]
        additional_context = {
            'default_composition_mode': 'mass_mail',
            'default_partner_to': '${object.id}',
            'active_model': dist_list.dst_model_id.model,
            'default_distribution_list_id': dist_list.id,
            'default_res_id': 0,
            'default_template_id': ref_template,
        }
        context.update(additional_context)

        return {
                'type': 'ir.actions.act_window',
                'name': _('Mass Mailing'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'mail.compose.message',
                'view_id': False,
                'context': context,
        }

    def get_ids_from_distribution_list(self, cr, uid, ids, safe_mode=True, context=None):
        """
        ==============================
        get_ids_from_distribution_list
        ==============================
        This method computes all filters result and return a list of ids depending of
        the ``bridge_field`` of the distribution list.
        :type safe_mode: boolean
        :param safe_mode: tool used in case of multiple distribution list.
                          If a filter is include into a distribution list and exclude into
                          an other then the result depends of `safe_mode`.
                          True: excluded are not present
                          False: excluded will be present if included into an other
        :raise orm.except_orm: many distribution list with different models
        """
        distribution_lists = self.browse(cr, uid, ids, context=context)
        if distribution_lists:
            model_target = distribution_lists[0].dst_model_id.model
            for dl in distribution_lists[1:]:
                if dl.dst_model_id.model != model_target:
                    raise orm.except_orm(_('Error'), _('Distribution lists are not compatible'))
                model_target = dl.dst_model_id.model

        l_to_include = {}
        l_to_exclude = {}

        included_ids = []
        excluded_ids = []
        res_ids = []
        for distribution_list in distribution_lists:
            # if no include are specified then get all the list of 'ids' from the destination model
            if not distribution_list.to_include_distribution_list_line_ids:
                model = distribution_list.dst_model_id.model
                result = self.pool.get(model).search(cr, uid, [], context=context)
                if model in l_to_include:
                    l_to_include[model] += result
                else:
                    l_to_include[model] = result
            else:
                # get all the ids to include
                for to_include in distribution_list.to_include_distribution_list_line_ids:
                    model, result = self.pool.get('distribution.list.line').get_ids_from_search(cr, uid, to_include, context=context)
                    if model in l_to_include:
                        l_to_include[model] += result
                    else:
                        l_to_include[model] = result

            # get all the ids to exclude
            for to_exclude in distribution_list.to_exclude_distribution_list_line_ids:
                model, result = self.pool.get('distribution.list.line').get_ids_from_search(cr, uid, to_exclude, context=context)
                if model in l_to_exclude:
                    l_to_exclude[model] += result
                else:
                    l_to_exclude[model] = result

            # case where there are multiple models: dst_model is 'into' the bridge_field
            if distribution_list.bridge_field != 'id':
                for key in l_to_include.keys():
                    result = self.pool[key].read(cr, uid, l_to_include[key], [distribution_list.bridge_field], context=context)
                    for r in result:
                        if r and r.get(distribution_list.bridge_field, False):
                            included_ids.append(r[distribution_list.bridge_field])

                for key in l_to_exclude.keys():
                    result = self.pool[key].read(cr, uid, l_to_exclude[key], [distribution_list.bridge_field], context=context)
                    for r in result:
                        if r and r.get(distribution_list.bridge_field, False):
                            excluded_ids.append(r[distribution_list.bridge_field])
            else:
                include_temp = l_to_include.values()
                if include_temp:
                    included_ids += include_temp[0]
                exclude_temp = l_to_exclude.values()
                if exclude_temp:
                    excluded_ids += exclude_temp[0]

            if not safe_mode:
                included_ids = set(included_ids)
                excluded_ids = set(excluded_ids)
                included_ids -= excluded_ids
                res_ids = res_ids + list(included_ids)

        if safe_mode:
            included_ids = set(included_ids)
            excluded_ids = set(excluded_ids)
            included_ids -= excluded_ids
        else:
            included_ids = set(res_ids)

        return list(included_ids)

    def get_mass_mailing_ids(self, cr, uid, ids, context=None):
        """
        ====================
        get_mass_mailing_ids
        ====================
        """
        res_ids = self.get_ids_from_distribution_list(cr, uid, ids, context=context)
        if context is None:
            context = {}
        if not context.get('field_mailing_object', False):
            return res_ids
        else:
            result_ids = []
            dls = self.browse(cr, uid, ids, context=context)
            if dls and res_ids:
                for trg_object in self.pool[dls[0].dst_model_id.model].browse(cr, uid, res_ids, context=context):
                    new_id = eval('trg_object.%s.id' % context.get('field_mailing_object'))
                    if new_id:
                        result_ids.append(new_id)
            return result_ids

    def complete_distribution_list(self, cr, uid, trg_dist_list_ids, src_dist_list_ids, context=None):
        """
        ==========================
        complete_distribution_list
        ==========================
        This method will allow to complete a target distribution list with the distribution list line
        of others.
        :type trg_dist_list_ids: [integer]
        :param trg_dist_list_ids: ids of the target distribution list
        :type src_dist_list_ids: [integer]
        :param src_dist_list_ids: ids of the distribution list that will complete the target
                                  distribution list
        **Note**
        Ex:
        1)  dl_trg | to_include:a
            dl_src | to_include:b   | to_exclude: c
            ---------------------------------------
            dl_trg | to_include: ab | to_exclude: c
        """
        for trg_dist_list_vals in self.read(cr, uid, trg_dist_list_ids, ['to_include_distribution_list_line_ids',
                                                                    'to_exclude_distribution_list_line_ids'],
                                                                    context=context):
            trg_l_to_include = trg_dist_list_vals['to_include_distribution_list_line_ids']
            trg_l_to_exclude = trg_dist_list_vals['to_exclude_distribution_list_line_ids']
            src_l_to_include = []
            src_l_to_exclude = []
            for src_dist_list_vals in self.read(cr, uid, src_dist_list_ids, ['to_include_distribution_list_line_ids',
                                                                        'to_exclude_distribution_list_line_ids'],
                                                                        context=context):
                src_l_to_include += src_dist_list_vals['to_include_distribution_list_line_ids']
                src_l_to_exclude += src_dist_list_vals['to_exclude_distribution_list_line_ids']
            trg_l_to_include += src_l_to_include
            trg_l_to_exclude += src_l_to_exclude
            trg_l_to_include = list(set(trg_l_to_include))
            trg_l_to_exclude = list(set(trg_l_to_exclude))
            vals = {}
            if trg_l_to_include:
                vals['to_include_distribution_list_line_ids'] = [[6, False, trg_l_to_include]]
            if trg_l_to_exclude:
                vals['to_exclude_distribution_list_line_ids'] = [[6, False, trg_l_to_exclude]]
            if vals:
                self.write(cr, uid, [trg_dist_list_vals['id']], vals, context=context)

    def get_action_from_domains(self, cr, uid, ids, context=None):
        """
        =======================
        get_action_from_domains
        =======================
        Allow to see result of a distribution list
        :rparam: ir.actions.act_window
        """
        dl = self.browse(cr, uid, ids, context=context)[0]
        res_ids = self.get_ids_from_distribution_list(cr, uid, ids, context=context)
        if not res_ids:
            res_ids = [-1]
        domain = "[['id', 'in', %s]]" % res_ids
        return {
                'type': 'ir.actions.act_window',
                'name': _(' Result of ' + dl.name + ' Distribution List'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': dl.dst_model_id.model,
                'view_id': False,
                'views': [(False, 'tree'),
                          (False, 'form')],
                'context': context,
                'domain': domain,
        }


class distribution_list_line(orm.Model):

    def _get_record(self, record_or_list):
        """
        pre: record_or_list is a browse_record list or a browse_record
        res: return the first element or the list or the element if not a list.
        """
        return record_or_list[0] if type(record_or_list) is orm.browse_record_list else record_or_list

    _name = 'distribution.list.line'
    _columns = {
        'name': fields.char(string='Name', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'domain': fields.text(string="Domain", required=True),
        'src_model_id': fields.many2one('ir.model', 'Source Model', required=True),
    }
    _sql_constraints = [('unique_name_by_company', 'unique(name,company_id)', 'Name Must Be Unique By Company')]
    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(cr, uid,
                                                          'distribution.list.line', context=c),
        'domain': "[]",
    }

    def save_domain(self, cr, uid, ids, domain, context=None):
        """
        pre: domain is initialized and contain a domain expression.
        post: the domain of the record with id ids is modified with domain.
        """
        self.write(cr, uid, ids, {'domain': domain}, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        post: if domain is empty then initialize it into the vals with '[]'
        """
        if not vals.get('domain'):
            vals['domain'] = '[]'
        return super(distribution_list_line, self).create(cr, uid, vals, context=None)

    def get_ids_from_search(self, cr, uid, record_line, context=None):
        """
        pre: record_line is a distribution_list_line record initialized
        res: the ids result of the search on 'model' with 'domain' (contained into record_line)
        """
        record_line = self._get_record(record_line)
        model = record_line.src_model_id.model
        try:
            return model, self.pool.get(model).search(cr, uid, eval(record_line.domain), context=context)
        except:
            raise orm.except_orm(_('Error'), _('The filter ') + record_line.name + _(' is invalid'))

    def get_list_from_domain(self, cr, uid, ids, context=None):
        """
        This method will provide a 'test' by returning a dictionary
        that allow user to see the result of the domain expression applied on the selected model
        """
        current_filter = self.browse(cr, uid, ids, context)
        current_filter = self._get_record(current_filter)
        # test if it works
        self.get_ids_from_search(cr, uid, current_filter, context=context)

        return {
                'type': 'ir.actions.act_window',
                'name': _(' Result of ' + current_filter.name + ' Filter'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': current_filter.src_model_id.model,
                'view_id': False,
                'views': [(False, 'tree'),
                          (False, 'form')],
                'context': context,
                'domain': current_filter.domain,
        }

    def action_partner_selection(self, cr, uid, ids, context=None):
        """
        res: Launch an action act_windows with special parameters:
               * view_mode      --> tree_partner_selection
                   View Customized With JavaScript and QWeb

               * flags          --> search_view
                   Put the search_view to true allow to show
                   The SearchBox into a PopUp window
        """
        if context is None:
            context = {}
        context.update({
            'res_id': ids,
        })
        ir_model_data = self.pool.get('ir.model.data')
        tree_view = ir_model_data.get_object_reference(cr, uid, 'base', 'view_partner_tree')[1]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partners List',
            'res_model': 'res.partner',
            'view_id': tree_view,
            'view_mode': 'tree_partner_selection',
            'target': 'new',
            'flags': {'search_view': True},
            'context': context,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
