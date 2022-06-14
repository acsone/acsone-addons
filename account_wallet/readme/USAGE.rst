Setup
-----
* Make sure you are in the group_account_manager (for setup at least)
* Make sure you are in the group Show Accounting Features - Readonly (for setup at least)
* Go to Accounting > Wallet -> Wallet Type
* Define first a Wallet type.
* For move lines generation, please:
    * Choose a sequence
    * Choose an account
    * Choose a product
    * Choose a journal

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet-type.png
   :width: 90%
   :alt: Wallet Type
   :align: center

* On the product, you have to set the same account on the "Income Account"

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet-product.png
   :width: 90%
   :alt: Wallet Product
   :align: center

* LIMITATION: The wallet product should not include taxes or
  taxes with amount <> 0.

Utilization
-----------

* Go to Accounting > Customer -> Invoice
* Create an invoice with the same product as your wallet type
* Save the invoice
* Go to Accounting > Wallet -> Wallet

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet-invoice.png
   :width: 90%
   :alt: Wallet Invoice
   :align: center

* A wallet is generated without any link to the customer with the amount as balance
  If the customer already have an active wallet, the credit goes on the same wallet
  The goal behind the 'anonymous' wallet is to give the opportunity to offer this wallet

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet-wallet.png
   :width: 90%
   :alt: Wallet Wallet
   :align: center

* If your business requires you to generate wallet for credit notes
* you can use the wizard :
* Make sure you have are in this group : 	Show Full Accounting Features

.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet_refund_1.png
   :width: 90%
   :alt: Wallet Refund
   :align: center
.. figure:: https://raw.githubusercontent.com/acsone/acsone-addons/wallet-documentation/account_wallet/static/description/wallet_refund2.png
   :width: 90%
   :alt: Wallet Refund
   :align: center
