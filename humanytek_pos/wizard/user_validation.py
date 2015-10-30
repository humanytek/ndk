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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import except_orm

class user_validation(osv.osv_memory):
    _name = "user.validation"
    _description = "Check the current user"
    _columns = {
        'password': fields.char('Password', required=True),
    }

    def check_user(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
  
        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')
  
        for data in self.browse(cr, uid, ids, context=context):
            db = cr.dbname
            login =  self.pool.get('res.users').browse(cr, uid, uid)[0].login
            env = {}
            result = self.pool.get('res.users').authenticate(db, login, data.password, env)
            if result != False:
                return self.pool.get('pos.order').refund(cr, uid, rec_id, context=context)
            else:
                raise except_orm(
                                _('Authentication Error!'),
                                _("Please enter a valid password!")
                            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
