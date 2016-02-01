.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==============
Workflow tasks
==============

This module automatically creates tasks when entering workflow activities.

In addition to workflow_activity_acion module, this one allow you to create tasks when an object enters on an activity.

Tasks must be configured on the activity concerned. It is possible to define a Deathline based on a date field and a critical delay during which the task is displayed in red.

To access a task, a user must:

1) be in a security group define in the Security page of the activity.
2) Have access to the object

Installation
============

To install this module, you need to:

 * apply this patch on your Odoo 8.0 sources
   https://github.com/acsone/odoo/tree/8.0-imp-workflow-ape

Usage
=====

* You need to configure task parameters on activities:

	.. figure:: static/description/workflow_task_1.png
	   :alt: Task configuration

* Tasks list view

	.. figure:: static/description/workflow_task_2.png
	   :alt: Task list view

* Tasks form view

	.. figure:: static/description/workflow_task_3.png
	   :alt: Task form view



Known issues / Roadmap
======================

Other (not urgent):
 * how to decide to which user (groups) the task is assigned/assignable.
 * delete tasks when deleting the underlying Odoo object / workflow

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Adrien Peiffer <adrien.peiffer@acsone.eu>

Maintainer
----------

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: http://www.acsone.eu

This module is maintained by ACSONE SA/NV.
