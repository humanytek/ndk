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

class import_info_ndk(osv.Model):

    _inherit = 'import.info'
    _description = 'Cambios en campos y modelos para Import Info'
    
    # 01/04/2015 (felix) Metodo original que construye numero de paquete aleatorio
    def make_sscc(self, cr, uid, context=None):
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.lot.tracking')
        try:
            return sequence + str(self.checksum(sequence))
        except Exception:
            return sequence
    
    _columns = {
        'ref_paquete': fields.char('Referencia de paquete', size=64)
    }
    _defaults = {
        'ref_paquete': make_sscc
    }
    
    # 01/04/2015 (felix) Metodo para crear modificado, cambiar campo Referencia de paquete
    def create(self, cr, uid, vals, context=None):
        pack_id = super(import_info_ndk, self).create(cr, uid, vals, context=context)
        pack = self.browse(cr, uid, pack_id, context=context)
        if pack.id:
            obj_stock_tracking = self.pool.get('stock.tracking')
            obj_stock_tracking.create(cr, uid, {'name':vals['ref_paquete'],'import_id':pack.id}, context)
        return pack_id
        
import_info_ndk()
