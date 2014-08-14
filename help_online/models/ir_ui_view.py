# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class view(orm.Model):
    _inherit = "ir.ui.view"

    _columns = {
        'doc': fields.boolean("Whether this view is a documentation page"),
    }

    _defaults = {
        'doc': False,
    }
