import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-acsone-acsone-addons",
    description="Meta package for acsone-acsone-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_wallet',
        'odoo14-addon-account_wallet_coupon',
        'odoo14-addon-account_wallet_no_negative',
        'odoo14-addon-account_wallet_sale',
        'odoo14-addon-account_wallet_sale_display_discount_amount',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
