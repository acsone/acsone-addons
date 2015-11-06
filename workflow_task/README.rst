.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==============
Workflow tasks
==============

This module automatically creates tasks when entering workflow activities.

Installation
============

To install this module, you need to:

 * apply this patch on your Odoo 8.0 sources
   https://github.com/acsone/odoo/tree/8.0-imp-workflow-ape

Configuration
=============

To configure this module, you need to:

 * enable "Create task" on selected workflow activities.

Usage
=====

To use this module, you need to:

 * go to ...

Known issues / Roadmap
======================

Tasks tree:
 * filter "Not closed" (active by default)
 * filter "Assigned to me"
 * color (gray: closed, black: started, blue: new, red: deadline <= today)

Refresh de la task après click sur un bouton dynamique (du kanban).
Pour qu'on voie qu'elle se cloture sans devoir faire refresh.

Other (not urgent):
 * how to decide to which user (groups) the task is assigned/assignable.
 * delete tasks when deleting the underlying Odoo object / workflow

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: http://www.acsone.eu

This module is maintained by ACSONE SA/NV.
