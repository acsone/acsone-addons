# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of event_mass_mailing, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     event_mass_mailing is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     event_mass_mailing is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with event_mass_mailing.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Event Mass Mailing',
    'version': '8.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'event',
        'mass_mailing',
    ],
    'description': """
Event Mass Mailing
==================
This module associates mass mailing concept with event mailing behavior by
* adding a `send invitation` action
* customizing email action of event with mass mailing
""",
    'images': [
    ],
    'data': [
        'views/event.xml'
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
