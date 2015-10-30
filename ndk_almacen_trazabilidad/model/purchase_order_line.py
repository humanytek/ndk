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

class purchase_order_line_ndk(osv.Model):

    _inherit = 'purchase.order.line'
    _description = 'Add fields and methods for requests of Nordika'
    
    # 11/09/2015 (felix) Method to converted the current price
    def _calc_price_unit(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            price_unit = i.price_unit
            currency_name = i.standard_price_currency_id.name
            currency_rate_silent = i.standard_price_currency_id.rate_silent
            if currency_name not in ['MXN',None] and price_unit > 0.00:
                res[i.id] = price_unit / currency_rate_silent
            else:
                res[i.id] = price_unit
        return res
    
    # 14/09/2015 (felix) Method to get currency ID MXN
    def _get_currency(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        obj_currency = self.pool.get('res.currency')
        mxn_currency = obj_currency.search(cr, uid, [('name', 'like', 'MXN')])
        id_currency = obj_currency.browse(cr, uid, mxn_currency[0], context)['id']
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = id_currency
        return res
        
    # 14/09/2015 (felix) Method to get currency ID MXN
    def _calc_converted_price_subtotal(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            res[i.id] = i.price_unit_converted * i.product_qty
        return res
            
    _columns = {
        'price_unit_converted': fields.function(_calc_price_unit, type='float', 
            string='Converted price unit', digits=(10,2)),
        'currency_converted_id': fields.function(_get_currency, type='many2one', 
            string='Converted currency', obj='res.currency'),
        'converted_price_subtotal': fields.function(_calc_converted_price_subtotal, 
            type='float', string='Subtotal price converted currency'),
        'percent_igi': fields.float('Percent IGI', digits=(10,2))
    }
    
    # 30/10/2015 (felix) Method to return values of "amount_igi"
    def on_change_percent_igi(self, cr, uid, ids, percent_igi, converted_price_subtotal, context=None):
        res = {}
        if percent_igi:
            amount_igi = converted_price_subtotal * percent_igi / 100
            res = {'amount_igi':amount_igi}
        return {'value':res}
    
purchase_order_line_ndk()
