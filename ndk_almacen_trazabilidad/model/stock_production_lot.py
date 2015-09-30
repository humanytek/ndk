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

class stock_production_lot_ndk(osv.Model):

    _inherit = 'stock.production.lot'
    _description = 'Add fields and methods for requests of Nordika'
    
    # 22/09/2015 (felix) Check lines of purchase orders to get price for each product
    # in the cost of serial number
    def _get_price(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            for l in i.move_ids:
                res[i.id] = l.price_unit
        return res
    
    # 22/09/2015 (felix) Check lines of purchase orders to get the currency for each product
    def _get_currency(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0
            for l in i.move_ids:
                res[i.id] = l.price_currency_id.id
        return res
    
    _columns = {
        'price': fields.function(_get_price, string='Price', type='float', 
            digits=(10,2)),
        'currency_id': fields.function(_get_currency, type='many2one', 
            obj='res.currency', string='Currency'),
    }
    
stock_production_lot_ndk()
