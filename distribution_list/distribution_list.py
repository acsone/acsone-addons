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

UNIQUE_DISTRIBUTION_LIST_ERROR_MSG = _(
    'The name of a distribution list must be unique. A distribution list '
    'with the same name already exists.')
UNIQUE_FILTER_ERROR_MSG = _(
    'The name of a filter must be unique. A filter with the same name already '
    'exists.')


class distribution_list(orm.Model):

    _name = 'distribution.list'

    def _get_computed_ids(self, cr, uid, bridge_field, to_be_computed_ids,
                          context=None):
        """
        Convert source ids to target ids according to the bridge field
        """
        computed_ids = []
        if bridge_field != 'id':
            for key in to_be_computed_ids.keys():
                result = self.pool[key].read(
                    cr, uid, to_be_computed_ids[key],
                    [bridge_field],
                    context=context)
                for r in result:
                    if r and r.get(bridge_field, False):
                        if isinstance(r[bridge_field],
                                      tuple):
                            computed_ids.append(
                                r[bridge_field][0])
                        else:
                            computed_ids.append(
                                r[bridge_field])
        else:
            for v in to_be_computed_ids.values():
                computed_ids += v
        return set(computed_ids)

    def _order_del(self, cr, uid, lst, context=None):
        """
        remove all duplicate elements from lst without corrupt the order

        :type lst: []
        :rtype: []
        """
        s = set()
        res_lst = []
        for el in lst:
            if el in s:
                continue
            else:
                s.add(el)
                res_lst.append(el)
        return res_lst

    _columns = {
        'id': fields.integer('ID'),
        'name': fields.char(string='Name', required=True),
        'to_include_distribution_list_line_ids': fields.many2many(
            'distribution.list.line',
            'include_distribution_list_line_rel',
            'include_distribution_list_id',
            'include_distribution_list_line_id', string="Filter To Include"),
        'to_exclude_distribution_list_line_ids': fields.many2many(
            'distribution.list.line',
            'exclude_distribution_list_line_rel',
            'exclude_distribution_list_id',
            'exclude_distribution_list_line_id', string="Filter To Exclude"),
        'company_id': fields.many2one('res.company', 'Company'),
        'dst_model_id': fields.many2one('ir.model', 'Destination Model',
                                        required=True),
        'bridge_field': fields.char(
            'Bridge Field', required=True,
            help="A common field name that make bridge between "
                 "source model of filters and target model of "
                 "distribution list"),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(
            cr, uid, 'distribution.list', context=c),
        'dst_model_id': lambda self, cr, uid, c:
        self.pool.get('ir.model').search(
            cr, uid, [('model', '=', 'res.partner')], context=c)[0],
        'bridge_field': 'id',
    }
    _sql_constraints = [('unique_name_by_company',
                         'unique(name,company_id)',
                         UNIQUE_DISTRIBUTION_LIST_ERROR_MSG)]

    def copy(self, cr, uid, _id, default=None, context=None):
        """ Reset the state and the registrations while copying an event
        """
        if not default:
            default = {}
        name = self.read(cr, uid, [_id], ['name'], context)[0]['name']
        default.update({'name': _('%s (copy)') % name})
        return super(distribution_list, self).copy(
            cr, uid, _id, default=default, context=context)

    def mass_mailing(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        dist_list = self.browse(cr, uid, ids, context=context)[0]
        ir_model_data = self.pool.get('ir.model.data')
        ref_template = ir_model_data.get_object_reference(
            cr, uid, 'distribution_list',
            'email_template_partner_distribution_list')[1]
        additional_context = {
            'default_composition_mode': 'mass_mail',
            'default_partner_to': '${object.id}',
            'active_model': dist_list.dst_model_id.model,
            'default_distribution_list_id': dist_list.id,
            'default_res_id': 0,
            'default_template_id': ref_template,
        }
        context.update(additional_context)

        return {'type': 'ir.actions.act_window',
                'name': _('Mass Mailing'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'mail.compose.message',
                'view_id': False,
                'context': context,
                }

    def get_ids_from_distribution_list(self, cr, uid, ids, safe_mode=True,
                                       context=None):
        """
        This method computes all filters result and return a list of ids
        depending of the ``bridge_field`` of the distribution list.

        :type safe_mode: boolean
        :param safe_mode: tool used in case of multiple distribution list.
                          If a filter is include into a distribution list
                          and exclude into an other then the result depends
                          of `safe_mode`.
                          True: excluded are not present
                          False: excluded will be present if included into an
                          other
        :raise orm.except_orm: many distribution list with different models
        """
        distribution_lists = self.browse(cr, uid, ids, context=context)
        if distribution_lists:
            model_target = distribution_lists[0].dst_model_id.model
            for dl in distribution_lists[1:]:
                if dl.dst_model_id.model != model_target:
                    raise orm.except_orm(
                        _('Error'), _('Distribution lists are not compatible'))
                model_target = dl.dst_model_id.model

        l_to_include = {}
        l_to_exclude = {}
        set_included_ids = set()

        included_ids = []
        excluded_ids = []
        res_ids = []
        dll_obj = self.pool.get('distribution.list.line')
        for distribution_list in distribution_lists:
            # if no include are specified then get all the list of 'ids'
            # from the destination model
            if not distribution_list.to_include_distribution_list_line_ids:
                model = distribution_list.dst_model_id.model
                result = self.pool.get(model).search(cr, uid, [],
                                                     context=context)
                if model in l_to_include:
                    l_to_include[model] += result
                else:
                    l_to_include[model] = result
            else:
                # get all the ids to include
                l_ids = distribution_list.to_include_distribution_list_line_ids
                for to_include in l_ids:
                    model, result = dll_obj.get_ids_from_search(
                        cr, uid, to_include, context=context)
                    if model in l_to_include:
                        l_to_include[model] += result
                    else:
                        l_to_include[model] = result

            # get all the ids to exclude
            l_ids = distribution_list.to_exclude_distribution_list_line_ids
            for to_exclude in l_ids:
                model, result = dll_obj.get_ids_from_search(
                    cr, uid, to_exclude, context=context)
                if model in l_to_exclude:
                    l_to_exclude[model] += result
                else:
                    l_to_exclude[model] = result

            if not safe_mode:
                res_ids = self._get_computed_ids(
                    cr, uid, distribution_list.bridge_field, l_to_exclude,
                    context=context)
                res_ids -= self._get_computed_ids(
                    cr, uid, distribution_list.bridge_field, l_to_include,
                    context=context)
                set_included_ids = set(list(set_included_ids) + list(res_ids))
                l_to_exclude = {}
                l_to_include = {}

        if safe_mode:
            set_included_ids = self._get_computed_ids(
                cr, uid, distribution_list.bridge_field, l_to_include,
                context=context)
            set_included_ids -= self._get_computed_ids(
                cr, uid, distribution_list.bridge_field, l_to_exclude,
                context=context)

        return list(set_included_ids)

    def get_complex_distribution_list_ids(self, cr, uid, ids, context=None):
        """
        Simple case:
            no ``field_main_object' into the context``.
            ``res_ids`` is result of ``get_ids_from_distribution_list``
            second list to return is void.
        Case of ``field_main_object' into the context`` into context:
            The resulting ids are not the ids computed by the
             ``get_ids_from_distribution_list``
            ``field_mailing_object`` is the name of a field into the
             distribution_list.trg_model
            The ``result_ids`` are therefore
            [trg_model.field_mailing_object.id]
        Case when ``more_filter`` is into the context: apply a second filter
        Case when ``order_by`` is into the context then apply an order into the
             search
            Aternative_ids is the second list to return.
            If ``field_alternative_object`` then try to add
            trg_model.field_alternative_object.id to the
            alternative_ids list.
        :rtype: [],[]
        :rparam: list of waiting ids for a distribution list
        """
        res_ids = self.get_ids_from_distribution_list(
            cr, uid, ids, context=context)
        alternative_ids = []
        if context is None:
            context = {}
        main_object = context.get('field_main_object', False)
        if main_object:
            alternative_object = context.get('field_alternative_object', False)
            result_ids = []
            dls = self.browse(cr, uid, ids, context=context)

            if dls:
                dls_target_model = dls[0].dst_model_id.model
            if dls_target_model and res_ids:
                domains = []
                if context.get('more_filter', False):
                    domains = context['more_filter']
                    domains.append("('id', 'in', %s)" % res_ids)
                domain_main_objects = domains + \
                    ["('%s', '<>', False)" % main_object]
                domain_main_objects = '[%s]' % ','.join(domain_main_objects)
                sort_by = context.get('sort_by', False)

                main_values = self.pool[dls_target_model].search_read(
                    cr, uid, eval(domain_main_objects),
                    fields=[main_object], order=sort_by, context=context)

                if main_values:
                    # extract id of field_main_object
                    result_ids = []
                    for val in main_values:
                        if isinstance(val[main_object], tuple):
                            result_ids.append(val[main_object][0])
                        else:
                            result_ids .append(val[main_object])
                if alternative_object:
                    domain_alternative_objects = domains + \
                        ["('%s', '=', False)" % main_object]
                    domain_alternative_objects = '[%s]' % ','.join(
                        domain_alternative_objects)

                    target_obj = self.pool[dls_target_model]
                    alternative_values = target_obj.search_read(
                        cr, uid, eval(domain_alternative_objects),
                        fields=[alternative_object], order=sort_by,
                        context=context)
                    if alternative_values:
                        # extract alternative values
                        alternative_ids = []
                        for val in alternative_values:
                            if isinstance(val[alternative_object], tuple):
                                alternative_ids.append(
                                    val[alternative_object][0])
                            else:
                                alternative_ids.append(
                                    val[alternative_object])
            res_ids = self._order_del(cr, uid, result_ids, context=context)
            alternative_ids = self._order_del(
                cr, uid, alternative_ids, context=context)

        return res_ids, alternative_ids

    def complete_distribution_list(self, cr, uid, trg_dist_list_ids,
                                   src_dist_list_ids, context=None):
        """
        This method will allow to complete a target distribution list with
        the distribution list line of others.

        :type trg_dist_list_ids: [integer]
        :param trg_dist_list_ids: ids of the target distribution list
        :type src_dist_list_ids: [integer]
        :param src_dist_list_ids: ids of the distribution list that will
                                  complete the target distribution list
        **Note**
        Ex:
        1)  dl_trg | to_include:a
            dl_src | to_include:b   | to_exclude: c
            ---------------------------------------
            dl_trg | to_include: ab | to_exclude: c
        """
        for trg_dist_list_vals in self.read(
            cr, uid, trg_dist_list_ids,
            ['to_include_distribution_list_line_ids',
             'to_exclude_distribution_list_line_ids'], context=context):
            trg_l_to_include = trg_dist_list_vals[
                'to_include_distribution_list_line_ids']
            trg_l_to_exclude = trg_dist_list_vals[
                'to_exclude_distribution_list_line_ids']
            src_l_to_include = []
            src_l_to_exclude = []
            for src_dist_list_vals in self.read(
                cr, uid, src_dist_list_ids,
                ['to_include_distribution_list_line_ids',
                 'to_exclude_distribution_list_line_ids'], context=context):
                src_l_to_include += src_dist_list_vals[
                    'to_include_distribution_list_line_ids']
                src_l_to_exclude += src_dist_list_vals[
                    'to_exclude_distribution_list_line_ids']
            trg_l_to_include += src_l_to_include
            trg_l_to_exclude += src_l_to_exclude
            trg_l_to_include = list(set(trg_l_to_include))
            trg_l_to_exclude = list(set(trg_l_to_exclude))
            vals = {}
            if trg_l_to_include:
                vals['to_include_distribution_list_line_ids'] = \
                    [[6, False, trg_l_to_include]]
            if trg_l_to_exclude:
                vals['to_exclude_distribution_list_line_ids'] = \
                    [[6, False, trg_l_to_exclude]]
            if vals:
                self.write(cr, uid, [trg_dist_list_vals['id']], vals,
                           context=context)

    def get_action_from_domains(self, cr, uid, ids, context=None):
        """
        Allow to preview resulting of distribution list

        :rtype: {}
        :rparam: dictionary to launch an ir.actions.act_window
        """
        dl = self.browse(cr, uid, ids, context=context)[0]
        res_ids = self.get_ids_from_distribution_list(cr, uid, ids,
                                                      context=context)
        domain = "[['id', 'in', %s]]" % res_ids
        return {'type': 'ir.actions.act_window',
                'name': _(' Result of ' + dl.name + ' Distribution List'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': dl.dst_model_id.model,
                'view_id': False,
                'views': [(False, 'tree')],
                'context': context,
                'domain': domain,
                'target': 'new',
                }


class distribution_list_line(orm.Model):

    def _get_record(self, record_or_list):
        """
        :type record_or_list: browse_record list or a browse_record
        :rtype: browse_record
        :rparam: first el of `record_or_list` if type is list otherwise
                `record_or_list` itself
        """
        if hasattr(record_or_list, '__iter__'):
            return record_or_list[0]
        return record_or_list

    _name = 'distribution.list.line'
    _columns = {
        'name': fields.char(string='Name', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'domain': fields.text(string="Expression", required=True),
        'src_model_id': fields.many2one('ir.model', 'Model',
                                        required=True),
    }
    _sql_constraints = [('unique_name_by_company', 'unique(name,company_id)',
                         UNIQUE_FILTER_ERROR_MSG)]
    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(
            cr, uid, 'distribution.list.line', context=c),
        'domain': "[]",
    }

    def onchange_src_model_id(self, cr, uid, ids, context=None):
        """
        When `src_model_id` is changed then domain must be reset
        to avoid inconsistency
        """
        return {
            'value': {
                'domain': '[]',
            }
        }

    def copy(self, cr, uid, _id, default=None, context=None):
        """
        When copying then add '(copy)' at the end of the name
        """
        if not default:
            default = {}
        name = self.read(cr, uid, [_id], ['name'], context)[0]['name']
        default.update({'name': _('%s (copy)') % name})
        return super(distribution_list_line, self).copy(
            cr, uid, _id, default=default, context=context)

    def save_domain(self, cr, uid, ids, domain, context=None):
        """
        This method will update `domain`

        :type domain: char
        :param domain: new domain value
        """
        self.write(cr, uid, ids, {'domain': domain}, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        post: if domain is empty then initialize it into the vals with '[]'
        """
        if not vals.get('domain'):
            vals['domain'] = '[]'
        return super(distribution_list_line, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        If `src_model_id` is changed and not `domain`
        Then reset domain to its default value: `[]`
        """
        if vals.get('src_model_id', False):
            if not vals.get('domain', False):
                vals['domain'] = '[]'
        return super(distribution_list_line, self).write(
            cr, uid, ids, vals, context=context)

    def get_ids_from_search(self, cr, uid, record_line, context=None):
        """
        pre: record_line is a distribution_list_line record initialized
        res: the ids result of the search on 'model' with 'domain' (contained
             into record_line)
        """
        record_line = self._get_record(record_line)
        model = record_line.src_model_id.model
        try:
            return model, self.pool.get(model).search(
                cr, uid, eval(record_line.domain), context=context)
        except:
            raise orm.except_orm(
                _('Error'),
                _('The filter ') + record_line.name + _(' is invalid'))

    def get_list_from_domain(self, cr, uid, ids, context=None):
        """
        This method will provide a 'test' by returning a dictionary
        that allow user to see the result of the domain expression applied on
        the selected model
        """
        current_filter = self.browse(cr, uid, ids, context)
        current_filter = self._get_record(current_filter)
        # test if it works
        self.get_ids_from_search(cr, uid, current_filter, context=context)

        return {'type': 'ir.actions.act_window',
                'name': _(' Result of ' + current_filter.name + ' Filter'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': current_filter.src_model_id.model,
                'view_id': False,
                'views': [(False, 'tree')],
                'context': context,
                'domain': current_filter.domain,
                'target': 'new',
                }

    def action_partner_selection(self, cr, uid, ids, context=None):
        """
        Launch an action act_windows with special parameters:
           * view_mode      --> tree_partner_selection
               View Customized With JavaScript and QWeb

           * flags          --> search_view
               Put the search_view to true allow to show
               The SearchBox into a PopUp window
        """
        context = context or {}
        context['res_id'] = ids

        dll = self.browse(cr, uid, ids, context=context)[0]

        return {
            'type': 'ir.actions.act_window',
            'name': '%s List' % dll.src_model_id.name,
            'res_model': '%s' % dll.src_model_id.model,
            'view_id': False,
            'view_mode': 'tree_selection',
            'target': 'new',
            'flags': {'search_view': True},
            'context': context,
        }
