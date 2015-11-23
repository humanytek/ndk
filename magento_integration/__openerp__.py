# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://www.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Magento Integration',
    'author': 'Openlabs Technologies & Consulting Pvt Ltd, Zesty Beanz Technologies Pvt Ltd',
    'version': '0.31',
    'depends': [
        'base',
        'sale',
        'mrp',
        'delivery',
    ],
    'website': 'http://www.zbeanztech.com',
    'category': 'Specific Industry Applications',
    'summary': 'Magento Integration',
    'description': """
This module integrates OpenERP with magento.
============================================

This will import the following:

* Product categories
* Products
* Customers
* Addresses
* Orders
    """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/test_connection.xml',
        'wizard/import_websites.xml',
        'wizard/import_catalog.xml',
        'wizard/update_catalog.xml',
        'wizard/import_orders.xml',
        'wizard/export_orders.xml',
        'wizard/import_carriers.xml',
        'wizard/export_inventory.xml',
        'wizard/export_tier_prices.xml',
        'wizard/export_shipment_status.xml',
        'wizard/export_catalog.xml',
        'wizard/export_customer.xml',
        'product.xml',
        'magento.xml',
        'sale.xml',
        'product_images_view.xml',
        'partner_view.xml',
    ],
    'css': [],
    'images': [],
    'demo': [],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: