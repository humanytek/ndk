# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'HMTK Terminal Punto de Venta',
    'version': '0.01',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    "description": """
Module to add changes in POS view

Details:
--------
* Automatization of the currency symbol for each product.
    """,    
    'author': 'Humanytek',
    'website': 'https://github.com/humanytek/ndk',
    'depends': [
        'hmtk_pos_customization'
    ],
    'data': [
    ],
    'css': [
        'static/src/css/pos.css'
    ],
    'demo_xml': [],
    'js': [
        'static/src/js/widget_base.js',
    ],
    'qweb': [
        #'static/src/xml/pos.xml'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
