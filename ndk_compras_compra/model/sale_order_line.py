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

class sale_order_line_ndk(osv.Model):

    _inherit = 'sale.order.line'
    _columns = {
        'discount_1': fields.float('Discount 1', digits=(3,2)),
        'discount_2': fields.float('Discount 2', digits=(3,2)),
        'discount_3': fields.float('Discount 3', digits=(3,2)),
        'discount_4': fields.float('Discount 4', digits=(3,2)),
    }
    
    # 07/09/2015 (felix) Metodo on_change para el cambio de descuento
    def on_change_discount(self, cr, uid, ids, price_unit, discount_1=0.00, 
        discount_2=0.00, discount_3=0.00, discount_4=0.00, context=None):
        res = 0.00
        
        if discount_1 > 0.00:
            price_1 = float(price_unit) - float(price_unit) * discount_1/100
            dis_res = (price_unit - price_1) * 100 / price_unit
        
        if discount_2 > 0.00:
            price_2 = float(price_1) - float(price_1) * discount_2/100
            dis_res = (price_unit - price_2) * 100 / price_unit
        
        if discount_3 > 0.00:
            price_3 = float(price_2) - float(price_2) * discount_3/100
            dis_res = (price_unit - price_3) * 100 / price_unit
        
        if discount_4 > 0.00:
            price_4 = float(price_3) - float(price_3) * discount_4/100
            dis_res = (price_unit - price_4) * 100 / price_unit
            
        if discount_1 == 0.00 and discount_2 == 0.00 and discount_3 == 0.00 and discount_4 == 0.00:
            dis_res = 0.00
        
        res = {'discount': dis_res}
        return {'value': res}

sale_order_line_ndk()
