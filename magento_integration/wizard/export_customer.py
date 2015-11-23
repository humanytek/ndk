# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://www.zbeanztech.com)
#    contact@zbeanztech.com
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

from openerp.osv import osv, fields

import threading

class export_customer(osv.osv_memory):
    
    _name = 'magento.instance.website.export_customer'
    _description = 'Export Customer'
    
    def export_customers(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        website_id = context.get('active_id')
        t = threading.Thread(target=partner_obj.export_customers_to_magento,
                             args=(cr, uid, website_id, context, True))
        t.daemon = True
        t.start()
        #partner_obj.export_customers_to_magento(cr, uid, website_id, context=context)
        return True
    
export_customer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: