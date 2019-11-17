.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Uses plus sign instead of dash as technical email separator to build bounce return paths
========================================================================================

This module was written to force the mass mailing module to build
```Return-Path``` header with a plus sign as technical email separator instead
of a dash.

This transformation is mandatory for mails servers that treat the dash as a
valid email account character (as in ```willem-alexander@koninkrijk.nl```)
instead of a technical escape character allowing to add optional parameters to
the real email account (as in
```catchall-bounces-543-kremlin@vladimir-putin.ru```).

Credits
=======

Contributors
------------

* Jonathan Nemry (<jonathan.nemry@acsone.eu>)
* Olivier Laurent (<olivier.laurent@acsone.eu>)

Maintainer
----------

.. image:: http://www.acsone.eu/logo.png
   :alt: Ascone Sa/Nv
   :target: http://www.acsone.eu

This module is maintained by ACSONE.
