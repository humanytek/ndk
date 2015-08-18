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
    'name': 'HMTK Magento/Configuración',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'description': """
Módulo de Magento

Detalles:
---------
* Crear botón especial para replicación de campo "Modelo" de base Magento a base OpenERP
    """,
    'author': 'Humanytek',
    'website': 'https://github.com/humanytek/ndk',
    'depends': [
        'base',
        'product',
        'stock',
        'magento_integration'
    ],
    'data': [
        # Seguridad y grupos
        
        # Data
        
        # View y menu
        'view/magento_instances.xml',
        'view/website.xml',
        'view/ventas_clientes.xml',
        'view/ventas_cotizaciones.xml',
        'view/almacen_productos.xml'
        
        # Reportes
    ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
