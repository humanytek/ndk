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

class sale_order_ndk(osv.Model):

    _inherit = 'sale.order'
    
    # 27/10/2015 (felix) Metodo para calcular Facturado
    def _calc_facturado(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            for j in i.invoice_ids:
                if j.state in ['open','paid']:
                    res[i.id] += j.amount_total
        return res
        
    # 27/10/2015 (felix) Metodo para calcular Pendiente por facturar
    def _calc_por_facturar(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            for j in i.invoice_ids:
                if j.state in ['open','paid']:
                    res[i.id] += j.residual
        return res
    
    _columns = {
        'invoice_ids': fields.one2many('account.invoice', 'order_id', 
            'Attached invoice'),
        'facturado': fields.function(_calc_facturado, type='float', 
            string='Facturado'),
        'por_facturar': fields.function(_calc_por_facturar, type='float', 
            string='Por facturar')
    }
    
    

sale_order_ndk()
