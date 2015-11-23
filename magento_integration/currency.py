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

from openerp.osv import osv
from openerp.tools.translate import _

class Currency(osv.osv):
    _inherit = 'res.currency'
    _description = "Currency" 

    def search_using_magento_code(self, cursor, user, code, context):
        """
        Searches for currency with given magento code.

        :param cursor: Database cursor
        :param user: ID of current user
        :param code: Currency code
        :param context: Application context
        :return: Browse record of currency if found else raises error
        """
        currency_ids = self.search(
            cursor, user, [
                ('name', '=', code)
            ], context=context
        )

        if not currency_ids:
            raise osv.except_osv(
                _('Not Found!'),
                _('Currency with code %s does not exists.' % code)
            )

        currency = self.browse(
            cursor, user, currency_ids[0], context=context
        )
        return currency

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: