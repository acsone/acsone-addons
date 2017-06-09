# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def migrate(cr, version):
    cr.execute(
        "UPDATE hr_holidays set "
        "number_of_hours_temp_manual=tmp_number_of_hours_temp")
    cr.execute(
        """ALTER TABLE hr_holidays DROP COLUMN "tmp_number_of_hours_temp" """)
