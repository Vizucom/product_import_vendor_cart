# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2017- Vizucom Oy (http://www.vizucom.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Vendor Shopping Cart Import',
    'category': 'Warehouse',
    'version': '0.1',
    'author': 'Vizucom Oy',
    'website': 'http://www.vizucom.com',
    'depends': ['product', 'purchase'],
    'description': """
Vendor Shopping Cart Import
===========================
 * Adds a new view for importing csv/excel shopping carts exported from websites of vendors
 * Intended as a lightweight alternative for the Odoo core's import, so that the end users can do simple imports without dealing with XML IDs
 * Supports updating and creating products
 * Automatically creates a product.supplierinfo row for the vendor
 * Vendor cart specific field mappings can be configured in Settings - Technical - Vendor Shopping Cart Import - Vendor Settings

""",
    'data': [
        'views/vendor_settings.xml',
        'wizard/product_import.xml'
    ],
}
