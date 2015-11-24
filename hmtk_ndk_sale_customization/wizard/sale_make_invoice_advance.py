##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import openerp.addons.decimal_precision as dp

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        inv_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        inv_id = inv_obj.create(cr, uid, inv_values, context=context)
        inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
        # add the invoice to the sales order's invoices
        sale_obj.write(cr, uid, sale_id, {'invoice_ids': [(4, inv_id)]}, context=context)
        return inv_id


    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hmtk_ndk_sale_customization', 'group_full_invoicing')[1]
        group = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
        picking_obj = self.pool.get('stock.picking')
        full_invoice_uids = [x.id for x in group.users]
        sale_obj = self.pool.get('sale.order')
        act_window = self.pool.get('ir.actions.act_window')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        picking_id = picking_obj.search(cr, uid, [('sale_id', '=', sale_ids[0])], context=context)
        if wizard.advance_payment_method == 'all':
            if picking_id:
                picking = picking_obj.browse(cr, uid, picking_id, context=context)[0]
                if uid in full_invoice_uids or picking.state == 'done':
                    # create the final invoices of the active sales orders
                    return super(sale_advance_payment_inv,self).create_invoices(cr, uid, ids, context=context)
                else:
                    raise osv.except_osv(_('Warning!'), _('You do not have permissions for full invoicing. You can create partial invoice. Select option other than Invoice the whole sales order.'))
            elif uid in full_invoice_uids:
                 return super(sale_advance_payment_inv,self).create_invoices(cr, uid, ids, context=context)
            else:
                  raise osv.except_osv(_('Warning!'), _('Allow full invoicing for this user under user groups to perform this action.'))     
        else:
            return super(sale_advance_payment_inv,self).create_invoices(cr, uid, ids, context=context)


sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
