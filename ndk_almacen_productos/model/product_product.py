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

class product_product_ndk(osv.Model):

    _inherit = 'product.product'
    _description = 'Cambios en campos y modelos para Productos'

    # 08/09/2015 (felix) Metodo para habilitar o deshabilitar disponibildad 
    # de producto en punto de venta
    def _get_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0
            value = False
            if i.qty_available > 0.00:
                res[i.id] = 1
                value = True
            self.write(cr, uid, [i.id], {'available_in_pos': value}, context)
        return res
    
    _columns = {
        'chk_available_in_pos': fields.function(_get_available, type='integer', 
            string='Available in POS'),
    }
        
    # 21/06/2015 (felix) Metodo original modificado para buscar por el nombre tecnico
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            # ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
            ids = self.search(cr, user, ['|',('default_code','ilike',name),('modelo_tec','ilike',name)], limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
product_product_ndk()
