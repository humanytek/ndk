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
    
    # 30/09/2015 (felix) Calcular resto del descuent y subtotal por cada linea de producto
    def _calc_discount_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            cant = i.product_uom_qty
            price = i.price_unit
            discount_amount = (i.price_unit * i.product_uom_qty) - i.price_subtotal
            res[i.id] = discount_amount
        return res
    
    _columns = {
        'discount_1': fields.float('Discount 1', digits=(3,2)),
        'discount_2': fields.float('Discount 2', digits=(3,2)),
        'discount_3': fields.float('Discount 3', digits=(3,2)),
        'discount_4': fields.float('Discount 4', digits=(3,2)),
        'discount_amount': fields.function(_calc_discount_amount, type='float', 
            string='Monto de descuento', digits=(10,2))
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
    
    # 30/09/2015 (felix) Metodo on_change para el cambio de campo name
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            # 30/09/2015 (felix) Cambiar description_sale por modelo_tec
            #if product_obj.description_sale:
            if product_obj.modelo_tec:
                #result['name'] += '\n'+product_obj.description_sale
                result['name'] += '\n'+product_obj.modelo_tec
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}

sale_order_line_ndk()
