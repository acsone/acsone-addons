import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-acsone-acsone-addons",
    description="Meta package for acsone-acsone-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-cagnotte_base',
        'odoo10-addon-cagnotte_coupon',
        'odoo10-addon-cagnotte_no_negative',
        'odoo10-addon-cagnotte_partner',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
