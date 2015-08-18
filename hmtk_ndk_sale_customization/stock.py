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

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    def action_process(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids, context=context)[0].sale_id
        if order.order_policy == 'manual':
            if order.invoiced:
                return super(stock_picking_out, self).action_process(cr, uid, ids, context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('The sales order has not been fully paid.'))
        else:
            return super(stock_picking_out, self).action_process(cr, uid, ids, context=context)
stock_picking_out()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
