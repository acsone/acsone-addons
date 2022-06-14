Setup
-----
* Go to Accounting > Wallet -> Wallet type
* For the type that will work with coupon -> check the select-box

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet_coupon/static/description/wallet-type-coupon.png
   :width: 90%
   :alt: Wallet Type Coupon
   :align: center

* once checked, all wallet generated for that type will receive a coupon_code

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet_coupon/static/description/wallet-type-wallet.png
   :width: 90%
   :alt: Wallet Coupon
   :align: center

Utilization
------------

* Now it's easier to give to you client the unique identifier of his wallet for him to use it later
* This module also give the possibility to pay an invoice with a coupon (based on code)
* On a 'To Pay' invoice, run the register payment and choose the correct journal
* If the "with_coupon_code" is selected on the wallet type corresponding to the selected journal
* a new field "coupon code" will be displayed on the form

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet_coupon/static/description/wallet-coupon-register-payment.png
   :width: 90%
   :alt: Wallet Coupon Register Payment
   :align: center
