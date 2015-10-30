# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 BroadTech IT Solutions.
#    (http://wwww.broadtech-innovations.com)
#    contact@boradtech-innovations.com
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

from openerp import api, models

class report_pos_session(models.AbstractModel):
    _name = 'report.humanytek_pos.report_pos_sessions'
    
    def _get_total_balance(self, statement_ids):
        amount_list  = [amount.total_entry_encoding for amount in statement_ids]
        return reduce(lambda x,y: x+y, amount_list)
    
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('humanytek_pos.report_pos_sessions')
        session_obj = self.env['pos.session']
        selected_invoices = session_obj.browse(self._ids)
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': selected_invoices,
            'get_total_balance': self._get_total_balance,
        }
        return report_obj.render('humanytek_pos.report_pos_sessions', docargs)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: