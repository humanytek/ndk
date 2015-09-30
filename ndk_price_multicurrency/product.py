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

from openerp.osv import fields, osv
import decimal_precision as dp

class product_product(osv.osv):

    _inherit = 'product.product'
    _description = """Add a field price list"""
    
    def _get_default_currecy(self, cr, uid, ids, context=None):
        user_pool = self.pool.get('res.users')
        user_obj = user_pool.browse(cr, uid, uid, context=context)
        return user_obj.company_id.currency_id.id
    
    _columns = {
        'list_price_currency_id': fields.many2one('res.currency', 
            'List Price Currency', required=True),
        'standard_price_currency_id': fields.many2one('res.currency', 
            'Standard Price Currency', required=True)
    }
    
    _defaults = {
        'list_price_currency_id': _get_default_currecy,
        'standard_price_currency_id': _get_default_currecy
    }
    
    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = context
        currency_pool = self.pool.get('res.currency')
        product_uom_pool = self.pool.get('product.uom')
        user_pool = self.pool.get('res.users')
        res = super(product_product,self).price_get(cr, uid, ids, ptype, context=context)
        if context.get('pricelist_curr_id', False) and ptype == 'list_price':
            pricelist_currency_id = context['pricelist_curr_id']
            for product_obj in self.browse(cr, uid, ids, context=context):
                product_currency_id = product_obj.list_price_currency_id.id
                product_list_price = product_obj.list_price or 0.00
                if pricelist_currency_id != product_currency_id:
                    product_price = currency_pool.compute(cr, uid, product_currency_id, pricelist_currency_id,
                                                          product_list_price, context=context)
                else:
                    product_price = product_list_price
                context.update({'skip_currency_convert': True})
                res.update({product_obj.id: product_price})
        return res
    
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
