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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
import re

class import_info_ndk(osv.Model):

    _inherit = 'import.info'
    _description = 'Cambios en campos y modelos para Stock Move'
    
    # 02/04/2015 (felix) Metodo original para modificar los dos puntos y el cero intermedio
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not len(ids):
            return []
                
        # Verificacion de los datos a pasar para construir nombre
        res = []
        for r in self.read(cr, uid, ids, ['name', 'ref_paquete'], context):
            import_name = self.browse(cr, uid, r['id'], context).name
            if import_name == None:
                import_name = ''
            if re.match('^\d',r['ref_paquete']):
                n_pack = re.split('^0*',r['ref_paquete'])
                r_pack = n_pack[1]
            else:
                r_pack = r['ref_paquete']
            name = str(r_pack)+'::'+str(import_name)
            res.append((r['id'], name))
            
        return res
    
        
        
import_info_ndk()
