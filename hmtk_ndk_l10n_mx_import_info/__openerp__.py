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
    'name': 'HMTK : Customs Information on lots: Customized for NDK branch',
    'version': '0.01',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    "description": """
Make relation between information of import with goverment.
With this module you will be able to make a relation between invoice and Information of importing transaction.
It will work as production lot make better control with quantities.""",
    
    'author': 'Humanytek',
    'website': 'http://www.humanytek.com',
    'depends': ['hmtk_l10n_mx_import_info_custom', 'stock', 'account', 'purchase'],
    'data': ['purchase_view.xml',
             'wizard/load_pos_view.xml',
             'import_info_view.xml',
             
             ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: