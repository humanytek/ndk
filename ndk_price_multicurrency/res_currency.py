# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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

from osv import osv

class res_currency(osv.osv):
    _inherit = 'res.currency'
    
    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount,
                round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=None):
        if context is None:
            context = {}
        if not context.get('skip_currency_convert', False):
            res = super(res_currency, self).compute(cr, uid, from_currency_id, to_currency_id, from_amount,
                                                    round, currency_rate_type_from, currency_rate_type_to,
                                                    context=context)
        else:
            res = from_amount
        return res
    
res_currency()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
