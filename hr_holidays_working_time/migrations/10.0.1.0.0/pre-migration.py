# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def migrate(cr, version):
    cr.execute(
        """ALTER TABLE hr_holidays ADD COLUMN "tmp_number_of_hours_temp"
           double precision""")
    cr.execute(
        "UPDATE hr_holidays set "
        "tmp_number_of_hours_temp=number_of_hours_temp")
