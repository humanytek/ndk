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
from osv import fields, osv
from openerp.tools.translate import _
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def copy(self, cr, uid, id, default=None, context=None):
        po_line = self.pool.get('purchase.order.line')
        res =  super(purchase_order, self).copy(cr, uid, id, default, context)
        if res:
            po = self.browse(cr, uid, res, context=context)
            if po.order_line:
                for line in po.order_line:
                   po_line.write(cr, uid, line.id, {'amount_of_expend': 0, 'amount_with_expense': 0,'amount_igi': 0,'impact': 0}) 
        return res
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        order_process_flag = 0
        order = self.browse(cr, uid, ids, context=context)[0]
        if order.order_line:
            for line in order.order_line:
                if line.amount_with_expense == 0:
                    order_process_flag = 1
                    break
            if not order_process_flag:
                res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('Import products must contain Amount of Expenditure'))
        return res
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit,
            'amount_igi': order_line.amount_igi,
            'expense_amount': order_line.amount_of_expend,
        }
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        real_price_unit = (order_line.price_unit or 0.0) + (order_line.amount_of_expend/ order_line.product_qty) + (order_line.amount_igi/order_line.product_qty)
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit  or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'amount_igi':order_line.amount_igi or 0.0,
            'expense_amount': order_line.amount_of_expend or 0.0,
        }
purchase_order()
class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _order = 'supplier_id'
    def _get_supplier_id(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        pos = self.browse(cr, uid, ids, context=context)
        for po in pos:
            supplier_id = False
            if po.order_id.partner_id:
                supplier_id = po.order_id.partner_id.id
            
            res[po.id] = supplier_id
        return res
    def _get_origin(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        pos = self.browse(cr, uid, ids, context=context)
        for po in pos:
            origin = ''
            if po.order_id.origin:
                origin = po.order_id.origin
            
            res[po.id] = origin
        return res
    def _get_volume(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        pos = self.browse(cr, uid, ids, context=context)
        for po in pos:
            volume = po.product_id.volume * po.product_qty
            
            res[po.id] = volume
        return res
    _columns = {
        'info_id': fields.many2one('import.info', 'Import Info'),
        'amount_igi': fields.float('Amount IGI'),
        'impact': fields.float('Impact'),
        'amount_of_expend': fields.float('Expenditure'),
        'amount_with_expense': fields.float('Amount with Expenses'),
        'supplier_id': fields.function(_get_supplier_id, type='many2one', string='Supplier', relation='res.partner', store= True),
        'cubic_metres': fields.function(_get_volume, type="float", string='Cubic metres'),
        'origin': fields.function(_get_origin, type='string', string='Source Document'),
        }
purchase_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: