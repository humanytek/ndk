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
class load_pos(osv.osv_memory):
    _name = 'load.pos.lines'
    _columns = {
        'po_lines': fields.many2many('purchase.order.line', 'load_purchase_line', 'load_id', 'purchase_id', 'Purchase Lines', required=True),
        }
    def import_pos(self, cr, uid, ids, context=None):
        import_info_pool = self.pool.get('import.info')
        data = self.read(cr, uid, ids, ['po_lines'])[0]
        po_lines = data['po_lines']
        active_id = context.get('active_id')
        if po_lines:
            for po_line in po_lines:
                import_info_pool.write(cr, uid, active_id, {'po_ids': [(4, po_line)]})
        return True
load_pos()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: