# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import pytz
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare
from openerp.tools.safe_eval import safe_eval as eval

import logging
_logger = logging.getLogger(__name__)

class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'
    _columns = {
        'standard_price_currency_id': fields.many2one('res.currency', 
            'Purchase Price Currency', required=True)
    }
    
    # 21/08/2015 (felix) Metodo original para agregar campos adicionales
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        if context is None:
            context = {}
        res_partner = self.pool.get('res.partner')
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        standard_price_currency_id = product.standard_price_currency_id.id
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, context)
        res.get('value',{}).update({                                                                     
                'standard_price_currency_id': standard_price_currency_id,                                           
            })
        res1 = self.on_change_currency(cr, uid, ids, standard_price_currency_id, price_unit, product_id, context=context)
        res.get('value',{}).update({'price_unit' : res1['value']['price_unit'] }) 
        return res
     
    # 21/08/2015 (felix) On_change de divisa en lineas de compra
    def on_change_currency(self, cr, uid, ids, standard_price_currency_id, price_unit, product_id, context=None):
        res = {'value': {'price_unit': price_unit or 0.0}}
        
        if not standard_price_currency_id:
            return res
        
        price = 0.00
        obj_currency = self.pool.get('res.currency')
        src_currency = obj_currency.search(cr, uid, [('id', '=', standard_price_currency_id)])
        obj_product = self.pool.get('product.product')
        src_product = obj_product.search(cr, uid, [('id', '=', product_id)])
        
        # Si la divisa es igual a la seleccionada toma el precio referencia por defecto
        if src_currency and src_product:
            currency_id = obj_currency.browse(cr, uid, src_currency[0], context)['id']
            prod_currency_id = obj_product.browse(cr, uid, src_product[0], context)['standard_price_currency_id']
            prod_list_price = obj_product.browse(cr, uid, src_product[0], context)['standard_price']
            if currency_id == prod_currency_id.id:
                res['value'].update({'price_unit': prod_list_price})
            else:
                tasa = obj_currency.browse(cr, uid, src_currency[0], context)['rate_silent']
                price = float(prod_list_price) * float(tasa)
                # Verifica si es peso mexicano y moneda de producto es dolar
                name = obj_currency.browse(cr, uid, src_currency[0], context)['name']
                if name == 'MXN' and prod_currency_id.name == 'USD':
                    price = float(prod_list_price) / float(prod_currency_id.rate_silent)
                res['value'].update({'price_unit': price})
        return res
    
purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
