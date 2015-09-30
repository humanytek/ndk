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

from osv import fields, osv
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'list_price_currency_id': fields.many2one('res.currency', 
            'List Price Currency', required=True)
    }        
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
                          name='', partner_id=False, lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):
        result = {}  
        pricelist_pool = self.pool.get('product.pricelist')
        product_pool = self.pool.get('product.product')
        warning_msgs = ""
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                    uom=uom, qty_uos=qty_uos, uos=uos,
                    name=name, partner_id=partner_id, lang=lang,
                    update_tax=update_tax, date_order=date_order,
                    packaging=packaging, fiscal_position=fiscal_position,
                    flag=flag, context=context)
        if product and pricelist:
            product_price = product_pool.browse(cr, uid, product, context)['list_price']
            currency_id = product_pool.browse(cr, uid, product, context)['list_price_currency_id']
            '''
            pricelist_obj = pricelist_pool.browse(cr, uid, pricelist, context=context)            
            price = pricelist_pool.price_get(cr, uid, [pricelist], product, qty or 1.0, partner_id,
                        {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        'pricelist_curr_id': pricelist_obj.currency_id.id,
                        })[pricelist]
            if price is False:
            '''
            if product_price is False:
                warn_msg = _("Couldn't find a pricelist line matching this product and quantity.\n"
                    "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                #res['value'].update({'price_unit': price})
                res['value'].update({'price_unit': product_price, 'list_price_currency_id': currency_id.id})
        return res

    # 21/08/2015 (felix) On_change de divisa en lineas de ventas
    def on_change_currency(self, cr, uid, ids, list_price_currency_id, price_unit, product_id, context=None):
        res = {}
        
        if not list_price_currency_id:
            return res
        
        price = 0.00
        obj_currency = self.pool.get('res.currency')
        src_currency = obj_currency.search(cr, uid, [('id', '=', list_price_currency_id)])
        obj_product = self.pool.get('product.product')
        src_product = obj_product.search(cr, uid, [('id', '=', product_id)])
        
        # Si la divisa es igual a la seleccionada toma el precio referencia por defecto
        if src_currency and src_product:
            currency_id = obj_currency.browse(cr, uid, src_currency[0], context)['id']
            prod_currency_id = obj_product.browse(cr, uid, src_product[0], context)['list_price_currency_id']
            prod_list_price = obj_product.browse(cr, uid, src_product[0], context)['list_price']
            if currency_id == prod_currency_id.id:
                res = {'price_unit': prod_list_price}
            else:
                tasa = obj_currency.browse(cr, uid, src_currency[0], context)['rate_silent']
                price = float(prod_list_price) * float(tasa)
                # Verifica si es peso mexicano y moneda de producto es dolar
                name = obj_currency.browse(cr, uid, src_currency[0], context)['name']
                if name == 'MXN' and prod_currency_id.name == 'USD':
                    price = float(prod_list_price) / float(prod_currency_id.rate_silent)
                res = {'price_unit': price}
            
        return {'value': res}
    
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
