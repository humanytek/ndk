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
    'name': 'HMTK Almacén/Trazabilidad',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'description': """
Módulo de Almacén menú Trazabilidad, modificado para agregar campos relacionados con requerimientos para Nordika.

Detalles:
---------
* Ocultar vista tree de gestión de pedimentos
* Crear campo numérico que identifica internamente en el sistema un paquete de pedimento
    """,
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': [
        'base',
        'stock',
        'purchase',
        'l10n_mx_import_info',
        'hmtk_l10n_mx_import_info_custom',
        'hmtk_ndk_l10n_mx_import_info',
    ],
    'data': [
        # Seguridad y grupos
        
        # Data
        
        # View y menu
        'view/numero_serie.xml',
        'view/control_pedimento.xml',
        'view/import_info_embalaje.xml',
        
        # Reportes
    ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
