# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "POS Account Wallet Coupon",
    "version": "14.0.1.0.0",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Point Of Sale,Accounting & Finance",
    "website": "https://acsone.eu",
    "maintainers": ["rousseldenis"],
    "depends": [
        "account_wallet_coupon",
        # TODO:
        # 'cagnotte_no_negative',
        "point_of_sale",
    ],
    "data": [
        "views/pos_order.xml",
        "views/pos_template.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
