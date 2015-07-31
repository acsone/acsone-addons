# -*- encoding: utf-8 -*-
import logging

__name__ = 'Renaming column "mail_alias_id" to "alias_id"'
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        # it is the installation of the module
        return
    SQL_QUERY = '''
    ALTER TABLE
        distribution_list
    RENAME COLUMN mail_alias_id TO alias_id
    '''
    cr.execute(SQL_QUERY)
