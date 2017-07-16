.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Vendor Shopping Cart Import
===========================

Adds a new wizard for importing csv/excel shopping carts exported from websites of vendors

* Intended as a lightweight alternative for the Odoo core's import, so that the end users can do simple imports without dealing with XML IDs
* Supports updating and creating products and their supplier info rows

Installation
============
* Just install this module

Configuration
=============
* Configure vendor cart specific field mappings at Settings - Technical - Vendor Shopping Cart Import - Vendor Settings. Set which columns of the file should be mapped to which product or supplier info fields.
* If the file contains currencies or units of measures, map them to their Odoo counterparts in the same view (e.g. PCE -> Unit(s), euro -> EUR)

Usage
=====
* Launch the import wizard from Inventory -> Import Vendor Shopping Cart
* Select a field mapping you have configured, and a local CSV/XLS file
* The file gets validated against the mapping. If everything is OK, you will see a list of products to be created/updated. In case of validation errors, a list of issues is shown.

Known issues / Roadmap
======================
* The importer has been tested with three different vendors' carts: Farnell, Phoenix Contact and Thorlabs. Whether getting other vendors' carts to work requires just a mapping configuration or some code depends on the file's format and complexity.

Credits
=======

Contributors
------------
* Timo Talvitie <timo@vizucom.com>

Maintainer
----------
.. image:: http://vizucom.com/logo.png
   :alt: Vizucom Oy
   :target: http://www.vizucom.com


This module is maintained by Vizucom Oy
