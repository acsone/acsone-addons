.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

========================
Workflow activity action
========================

This module adds the concept of actions directly on the activities of an object.

It is now possible to define a list of actions on workflow activities.
Currently, these actions are configured as Odoo server action.

Once defined actions on activities, it is possible to use these ones directly on the object associated with the activity.
technically, it is necessary to make an inheritance of an abstract model and to add a field in the view of the object concerned.

You can define two types of security rules for the actions of management.

1) It is possible to define a security group list on the activity. For a user to perform an action on that activity, it must be defined in at least one group.
2) In addition to the first level, it is possible to define a list of activity record rule. The evaluation process of these security rules is similar to the ir.rule model.

Once the rules are evaluated, the actions are performed by super user (with base_suspend_security module)

Usage
=====

Here is an example implementation on account.invoice model.

* A python class ::

	from openerp import fields, models


	class AccountInvoice(models.Model)
	    _name = 'account.invoice'
	    _inherit = ['accont.invoice', 'workflow.action.model']

* An XML view ::

	<record model="ir.ui.view" id="invoice_form">
	    <field name="name">account.invoice.form</field>
	    <field name="model">account.invoice</field>
	    <field name="inherit_id" ref="account.invoice_form" />
	     <field name="arch" type="xml">
		<xpath expr="//header" position="attributes">
		    <attribute name="invisible">1</attribute>
		</xpath>
		<xpath expr="//header" position="after">
		    <header>
		        <field name="activity_action_ids" widget="many2many_action_buttons" />
		        <field name="state" widget="statusbar"/>
		    </header>
		</xpath>
	    </field>
	</record>

* Configuration of activities:

	.. figure:: static/description/workflow_activity_action_1.png
	   :alt: Configuration of activities

* Add a server action on activity

	.. figure:: static/description/workflow_activity_action_2.png
	   :alt: Add a server action on activity

* Using actions directly on the object:

	.. figure:: static/description/workflow_activity_action_3.png
	   :alt: Using actions directly on the object

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
