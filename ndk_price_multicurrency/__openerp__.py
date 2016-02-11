# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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
    'name': 'HMTK Multicurrency Prices',
    'sequence': 1,
    'version': '1.5',
    'author': 'Humanytek',
    'website': 'http://github.com/humanytek/ndk',
    'category': 'Sales Management',
    'depends': [
        'sale',
        'sale_stock',
        'product',
        'purchase',
        'account_accountant'
    ],
    'description': """Add developing for Nordika

Details
-------
* Create fields to define currency at product price of sale
* Create fields to define currency at product price of purchase
    """,
    'init_xml': [],
    'update_xml': [
        'product_view.xml',
        'sale_view.xml',
        'purchase_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'complexity': 'easy'
}
