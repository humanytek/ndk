# -*- coding: utf-8 -*-
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
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_currency(osv.osv):
    _inherit = "res.currency"
    _description = "Currency"
    
    def _current_valor(self, cr, uid, ids, name, arg, context=None):
        return self._current_valor_computation(cr, uid, ids, name, arg, False, context=context)

    def _current_valor_computation(self, cr, uid, ids, name, arg, raise_on_no_rate, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date' in context:
            date = context['date']
        else:
            date = time.strftime('%Y-%m-%d')
        date = date or time.strftime('%Y-%m-%d')
        # Convert False values to None ...
        currency_rate_type = context.get('currency_rate_type_id') or None
        # ... and use 'is NULL' instead of '= some-id'.
        operator = '=' if currency_rate_type else 'is'
        for id in ids:
            cr.execute("SELECT currency_id, valor FROM res_currency_rate WHERE currency_id = %s AND name <= %s AND currency_rate_type_id " + operator +" %s ORDER BY name desc LIMIT 1" ,(id, date, currency_rate_type))
            if cr.rowcount:
                id, valor = cr.fetchall()[0]
                res[id] = valor
            elif not raise_on_no_rate:
                res[id] = 0
            else:
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency %d for the given period" % (id)))
        return res
    
    _columns = {
        'valor': fields.function(_current_valor, string='Valor', digits=(12,6)),
    }
        
res_currency()


class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"
    _description = "Currency Rate"

    _columns = {
        'valor': fields.float('Valor', digits=(12,6)),
    }
    
res_currency_rate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
