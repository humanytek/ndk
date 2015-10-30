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
            
    # 17/09/2015 (felix) Modified methods made by hindues    
    def _calculate_volume(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total += po_id.product_id.volume * po_id.product_qty
            total = total
            res[info_record.id] = total
        return res
    
    def _calculate_total_qty(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total += po_id.product_qty
            res[info_record.id] = total
        return res
    
    def _calculate_total_expense(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total += po_id.amount_with_expense
            res[info_record.id] = total
            
        return res
    
    def _calculate_total_without_expense(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total +=  po_id.converted_price_subtotal
                    #total +=  po_id.price_subtotal
            res[info_record.id] = total
        return res
    
    def _calculate_cost_base_value(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total +=  po_id.price_unit
            res[info_record.id] = total
        return res
    
    def _calculate_cost_totals(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total +=  po_id.converted_price_subtotal + po_id.amount_igi
                    #total +=  po_id.price_subtotal + po_id.amount_igi
            res[info_record.id] = total
        return res
    
    def _calculate_grand_total(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = info_record.total_expense
            res[info_record.id] = total
        return res
    
    def load_purchase_products(self, cr, uid, ids, context=None):
        import_info = self.browse(cr, uid, ids, context=context)[0]
        product_import_obj = self.pool.get('product.import.info')
        if import_info.po_ids:
            for po in import_info.po_ids:
                data = {
                    'import_id': import_info.id,
                    'product_id': po.product_id.id,
                    'uom_id': po.product_uom.id,
                    'qty': po.product_qty,
                    'po_line': po.id,
                }
                if po.product_id.pack_control:
                    product_import_info_ids =  product_import_obj.search(cr, uid, [('import_id', '=', import_info.id), ('po_line', '=', po.id)])
                    if not product_import_info_ids:
                        product_import_obj.create(cr, uid, data, context=context)
                    else:
                        product_import_obj.write(cr, uid, product_import_info_ids, data, context=context)
                else:
                    raise osv.except_osv(_('Warning!'), _('This product is not importable.'))
        return True
    
    def calculate_button_all(self, cr, uid, ids, context=None):
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        for id in ids:
            info_record = self.browse(cr, uid, id, context=context)
            if info_record.po_ids:
                for po in info_record.po_ids:
                    #expense_amount = info_record.expense_amount
                    expense_amount = info_record.converted_expense_amount
                    line_expense = po.converted_price_subtotal
                    #line_expense =  po.price_subtotal
                    factor = line_expense / expense_amount
                    percentage = factor * 100
                    purchase_order_line_obj.write(cr, uid, po.id, {'impact': percentage}, context=context)
                    if info_record.expense_amount:
                        line_expense_wo = info_record.impact * factor
                        purchase_order_line_obj.write(cr, uid, po.id, {'amount_of_expend': line_expense_wo}, context=context)
                        amount_with_expenses = po.amount_of_expend + po.converted_price_subtotal + po.amount_igi
                        #amount_with_expenses = po.amount_of_expend + po.price_subtotal + po.amount_igi
                        purchase_order_line_obj.write(cr, uid, po.id, {'amount_with_expense': amount_with_expenses}, context=context)
        return True
        
    # 28/10/2015 (felix) Method to convert
    def _calc_converted_expense_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            for j in i.po_ids:
                res[i.id] += j.converted_price_subtotal
        return res
    
    _columns = {
        'ref_paquete': fields.char('Referencia de paquete', size=64),
        'name': fields.char('Number of Operation', size=128),
        'converted_expense_amount': fields.function(_calc_converted_expense_amount, 
            type='float', string='Converted expense amount', digits=(10,2))
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
