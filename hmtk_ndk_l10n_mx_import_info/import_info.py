# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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
class product_import_info(osv.osv):
    _inherit = 'product.import.info'
    _columns = {
        'po_line': fields.many2one('purchase.order.line', 'Line'),
        }
product_import_info()

class import_info(osv.Model):
    _inherit = 'import.info'
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
                    total +=  po_id.product_qty
            res[info_record.id] = total
        return res
    
    def _calculate_total_expense(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total +=  po_id.amount_with_expense
            res[info_record.id] = total
            
        return res
    def _calculate_total_without_expense(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        info_records = self.browse(cr, uid, ids, context=context)
        for info_record in info_records:
            total = 0
            if info_record.po_ids:
                for po_id in info_record.po_ids:
                    total +=  po_id.price_subtotal
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
                    total +=  po_id.price_subtotal + po_id.amount_igi
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
                    expense_amount = info_record.expense_amount
                    line_expense =  po.price_subtotal
                    factor = line_expense/expense_amount
                    percentage = factor*100
                    purchase_order_line_obj.write(cr, uid, po.id, {'impact' : percentage}, context=context)
                    if info_record.expense_amount:
                        line_expense_wo = info_record.impact * factor
                        purchase_order_line_obj.write(cr, uid, po.id, {'amount_of_expend' : line_expense_wo}, context=context)
                        amount_with_expenses = po.amount_of_expend + po.price_subtotal + po.amount_igi
                        purchase_order_line_obj.write(cr, uid, po.id, {'amount_with_expense' : amount_with_expenses}, context=context)
        return True
        
    _columns = {
        'total_qty': fields.function(_calculate_total_qty, type='float', string='Total Quantity'),
        'cost_base_qty': fields.float('Costs Base Quantity'),
        'cost_base_value': fields.function(_calculate_cost_base_value, type='float', string='Costs Base Value'),
        'cost_lines': fields.float('Cost Lines'),
        'cost_total': fields.function(_calculate_cost_totals, type='float', string='Costs Total'),
        'amount_igi': fields.char('Amount IGI', size=64),
        'po_ids': fields.one2many('purchase.order.line', 'info_id', 'Purchase Order Lines'),
        'sum_cubic_mts': fields.function(_calculate_volume, type='float', string='Sum of cubic meters'),
        'impact': fields.float('Impact Amount'),
        'expense_amount':fields.function(_calculate_total_without_expense, type='float', string='Amount without Expenses'),
        'total_expense': fields.function(_calculate_total_expense, type='float', string='Amount with Expenses'),
        'grand_total': fields.function(_calculate_grand_total, type='float', string='Total'),
        
        
        }
import_info()

class import_info_custom(osv.Model):
    _inherit = 'import.info.custom'
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['custom_name','number'], context=context)
        res = []
        for record in reads:
            name = record['custom_name']
            number = record['number']
            if name and number:
                
                name = '[ '+number+' ] - '+name
            elif name and  not number:
                name = '[ '+name+' ]'
            elif number and not name:
                name = '[ '+number+' ]'
            res.append((record['id'], name))
        return res
    
import_info_custom()   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: