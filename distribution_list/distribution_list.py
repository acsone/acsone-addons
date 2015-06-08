# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of distribution_list, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     distribution_list is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     distribution_list is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with distribution_list.
#     If not, see <http://www.gnu.org/licenses/>.
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
DEFAULT_BRIDGE_FIELD = 'id'


class distribution_list(orm.Model):

    _name = 'distribution.list'
    _description = 'Distribution List'

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
            'include_distribution_list_line_id', string="Filters to Include"),
        'to_exclude_distribution_list_line_ids': fields.many2many(
            'distribution.list.line',
            'exclude_distribution_list_line_rel',
            'exclude_distribution_list_id',
            'exclude_distribution_list_line_id', string="Filters to Exclude"),
        'company_id': fields.many2one('res.company', 'Company'),
        'dst_model_id': fields.many2one('ir.model', 'Destination Model',
                                        required=True),
        'bridge_field': fields.char(
            'Bridge Field', required=True,
            help="Field name making the bridge between "
                 "source model of filters and target model of "
                 "distribution list"),
        'note': fields.text('Notes'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(
            cr, uid, 'distribution.list', context=c),
        'dst_model_id': lambda self, cr, uid, c:
        self.pool.get('ir.model').search(
            cr, uid, [('model', '=', 'res.partner')], context=c)[0],
        'bridge_field': DEFAULT_BRIDGE_FIELD,
    }

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
        :raise orm.except_orm: several distribution lists with different models
                          or bridge fields
        """
        target_model = False
        bridge_field = False
        l_to_include = {}
        l_to_exclude = {}
        set_included_ids = set()

        dll_obj = self.pool.get('distribution.list.line')
        for distribution_list in self.browse(cr, uid, ids, context=context):
            # check for distribution lists compatibility
            target_model = target_model or distribution_list.dst_model_id.model
            bridge_field = bridge_field or distribution_list.bridge_field
            if (bridge_field, distribution_list.dst_model_id.model) != \
               (distribution_list.bridge_field, target_model):
                raise orm.except_orm(
                    _('Error'), _('Distribution lists are incompatible'))

            if not distribution_list.to_include_distribution_list_line_ids:
                # without included filters get all ids
                # from the destination model
                model = distribution_list.dst_model_id.model
                result = self.pool.get(model).search(cr, uid, [],
                                                     context=context)
                lst = l_to_include.setdefault(model, [])
                lst += result
                bridge_field = DEFAULT_BRIDGE_FIELD
            else:
                # get all ids to include
                l_ids = distribution_list.to_include_distribution_list_line_ids
                for to_include in l_ids:
                    model, result = dll_obj.get_ids_from_search(
                        cr, uid, to_include, context=context)
                    lst = l_to_include.setdefault(model, [])
                    lst += result

            # get all ids to exclude
            l_ids = distribution_list.to_exclude_distribution_list_line_ids
            for to_exclude in l_ids:
                model, result = dll_obj.get_ids_from_search(
                    cr, uid, to_exclude, context=context)
                lst = l_to_exclude.setdefault(model, [])
                lst += result

            if not safe_mode:
                # compute ids locally for only one distribution list
                res_ids = self._get_computed_ids(
                    cr, uid, bridge_field, l_to_include, context=context)
                res_ids -= self._get_computed_ids(
                    cr, uid, bridge_field, l_to_exclude, context=context)
                set_included_ids |= res_ids
                l_to_exclude = {}
                l_to_include = {}

        if bridge_field and safe_mode:
            # compute ids globally for all distribution lists
            set_included_ids = self._get_computed_ids(
                cr, uid, bridge_field, l_to_include, context=context)
            set_included_ids -= self._get_computed_ids(
                cr, uid, bridge_field, l_to_exclude, context=context)

        return list(set_included_ids)

    def _get_ids(self, cr, uid, ids, model, fld, dom, sort, context=None):
        """
        From an initial list of ids of a model, returns a list
        containing the value of a specific field of this model
        optionally filtered by an extra domain and/or
        ordered by a given sort criteria
        Final result is a list of unique values (sorted or not)
        If no target field is given the initial ids list is returned
        """
        res_ids = []
        if ids and model:
            if not fld:
                res_ids = ids
            else:
                domain = [('id', 'in', ids), (fld, '!=', False)]
                domain += dom or []

                vals = self.pool[model].search_read(
                    cr, uid, domain, fields=[fld], order=sort, context=context)
                if vals:
                    # extract id of fld
                    for val in vals:
                        if isinstance(val[fld], tuple):
                            res_ids.append(val[fld][0])
                        else:
                            res_ids.append(val[fld])
                res_ids = self._order_del(cr, uid, res_ids, context=context)

        return res_ids

    def get_complex_distribution_list_ids(self, cr, uid, ids, context=None):
        """
        Simple case:
            no ``field_main_object`` provided
            first result list is coming from ``get_ids_from_distribution_list``
            second result list is empty.
        If ``field_main_object`` is provided:
            the result ids are filtered according to the target model
            and the field specified, i.e. [trg_model.field_mailing_object.id]
        If ``more_filter`` is provided:
            apply a second filter
        If ``field_alternative_object`` is provided:
            a second result is computed from the first ids,
            i.e. [trg_model.field_alternative_object.id]
        If ``alternative_more_filter`` is provided:
            apply a second filter for the alternative object
        If ``sort_by`` is provided result ids are sorted accordingly
        :rtype: [],[]
        :rparam: expected main and alternative ids
        """
        context = context or {}
        res_ids = self.get_ids_from_distribution_list(
            cr, uid, ids, context=context)

        main_ids = []
        alternative_ids = []
        if ids and res_ids:
            dls = self.browse(cr, uid, ids, context=context)
            model = dls[0].dst_model_id.model
            sort = context.get('sort_by', False)

            main_ids = self._get_ids(
                cr, uid, res_ids, model,
                context.get('field_main_object'),
                context.get('more_filter'),
                sort, context=context)

            alternative_ids = self._get_ids(
                cr, uid, res_ids, model,
                context.get('field_alternative_object'),
                context.get('alternative_more_filter'),
                sort, context=context)

        return main_ids, alternative_ids

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
                'name': _('Result of %s') % dl.name,
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': dl.dst_model_id.model,
                'view_id': False,
                'views': [(False, 'tree')],
                'context': context,
                'domain': domain,
                'target': 'current',
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
    _description = 'Distribution List Line'

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
        'src_model_id': lambda self, cr, uid, c:
            self.pool.get('ir.model').search(
            cr, uid, [('model', '=', 'res.partner')], context=c)[0],
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
        if vals.get('src_model_id'):
            if not vals.get('domain'):
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
                _('The filter %s is invalid') % record_line.name)

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
                'name': _('Result of %s') % current_filter.name,
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': current_filter.src_model_id.model,
                'view_id': False,
                'views': [(False, 'tree')],
                'context': context,
                'domain': current_filter.domain,
                'target': 'current',
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
            'res_model': dll.src_model_id.model,
            'view_id': False,
            'view_mode': 'tree_selection',
            'target': 'new',
            'flags': {'search_view': True},
            'context': context,
        }
