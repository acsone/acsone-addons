# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_embedded_picture,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_embedded_picture is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_embedded_picture is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_embedded_picture.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Mail Embedded Picture",
    'summary': """
        This module set picture attachments as embedded part of mails
    """,
    'author': "ACSONE SA/NV",
    'website': "http://acsone.eu",
    'category': 'Mail',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
        'mass_mailing',
    ],
    'installable': True,
    'auto_install': False,
}
