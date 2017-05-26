# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Cagnotte Base",
    "version": "10.0.1.0.0",
    'author': "ACSONE SA/NV",
    "category": "Accounting & Finance",
    "website": "http://www.acsone.eu",
    "depends": [
        "account",
    ],
    "data": [
        "views/cagnotte_views.xml",
        "security/ir.model.access.csv",
        "security/cagnotte_base_security.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
