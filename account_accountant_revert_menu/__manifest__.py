# Copyright 2019 ACSONE SA/NV
# License Other proprietary.

{
    "name": "Account Accountant Revert Menu",
    "description": """
        This addon improves the compatibility of Enterprise accounting.

        A better alternative to this addon is to lookup the parent menu entries like this
        (credit Martin Trigaux - https://github.com/OCA/l10n-spain/pull/2094#issuecomment-1030125850):

        ```
        <record id="menu_root_aeat" model="ir.ui.menu">
            ...
            <!-- parent of the "Customers" menu -->
            <field name="parent_id" search="[('child_id', 'in', ref('account.menu_finance_receivables'))]" />
        </record>
        ```
    """,
    "version": "14.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["account", "account_accountant"],
    "data": ["data/account_accountant_data.xml"],
}
