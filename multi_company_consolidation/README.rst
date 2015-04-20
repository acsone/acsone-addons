.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Account reports multi company consolidation
===========================================


This module add a flag on account.fiscalyear to mark periods that are used for multi-company consolidation.

This flag is used in  accounts query processing (debit, credit, balance) to enable queries across fiscal years of different companies.

Be carefull, this module redefines 2 functions from base:

* `_get_balance` from 'account.financial.report'::

    """ Re-implementation of _get_balance for performance by pre-fetching the accounts.

        This method behaves like the original except it restricts the query to the
        chart_account_id that is present in the context if any. This is correct, as mixing accounts
        from different account charts does not make sense: when necessary this is done through
        consolidation children, which works with this method."""

* `_get_lines` from 'report.account.report_financial'::

    """ Override the official account_financial_report algorithm for performance
        - pre-fetch accounts
        - limit account details to the selected account chart
        Plus: prefix consolidation children accounts with the account plan name"""


Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Laurent Mignon <laurent.mignon@acsone.eu>

Maintainer
----------

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: http://www.acsone.eu

This module is maintained by the ACSONE SA/NV.
