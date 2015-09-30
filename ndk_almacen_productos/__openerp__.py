# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Humanytek (<http://humanytek.com>).
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
    'name': 'HMTK Almacén/Productos',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'description': """
Módulo de Almacén/Productos modificado para agregar campos relacionados con requerimientos para Nordika.

Detalles:
---------
* Discriminar búsquedas por modelo técnico de productos
    """,
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': [
        'base',
        'product',
        'stock',
        'magento_integration',
        'ndk_magento_configuracion',
        'point_of_sale',
    ],
    'data': [
        # Seguridad y grupos
        
        # Data
        
        # View y menu
        'view/productos.xml',
        
        # Reportes
    ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
