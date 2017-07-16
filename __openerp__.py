# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017- Vizucom Oy (http://www.vizucom.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html.
#
##############################################################################
{
    'name': 'Vendor Shopping Cart Import',
    'summary': 'Adds a new wizard for importing csv/excel shopping carts exported from websites of vendors',
    'version': '9.0.1.0.0',
    'category': 'Warehouse',
    'website': 'http://www.vizucom.com',
    'author': 'Vizucom Oy',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'product',
        'purchase'
    ],
    'data': [
        'views/vendor_settings.xml',
        'wizard/product_import.xml'
    ],
}
