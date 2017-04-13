# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def migrate(cr, version):
    cr.execute(
        """ALTER TABLE hr_holidays ADD COLUMN "set_hours_manually" BOOLEAN""")
    cr.execute("UPDATE hr_holidays set set_hours_manually='t'")
    cr.execute(
        "ALTER TABLE hr_holidays ADD COLUMN 'number_of_hours_temp_manual' "
        "double precision")
    cr.execute(
        "UPDATE hr_holidays set "
        "number_of_hours_temp_manual=number_of_hours_temp")
