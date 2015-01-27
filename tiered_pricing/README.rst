Tiered Pricing Management
==========================
This module allows to apply tiered pricing rules through pricelist management.

It is highly recommanded to update 'Product Price' decimal precision up to 6
digits.

Sample:
-------
Tiered Pricing:

* 01-20 = 10.0 € per widget
* 21-30 =  8.5 € per widget
* 31-40 =  7.0 € per widget
* 41+   =  5.5 € per widget

For a sale of 60 widgets, the final price will be computed like:

(20*10) + (10*8.5) + (10*7) + (20*5.5) = 465 €

Credits
-------

Author:

* Cédric Pigeon (ACSONE)

Contributors: 

