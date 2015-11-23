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

class ImportOrders(osv.TransientModel):
    _name = 'magento.store.store_view.import_orders'
    _description = 'Import orders'

    def import_orders(self, cursor, user, ids, context):
        """
        Import sale orders from magento for the current store view.

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        """
        store_view_obj = self.pool.get('magento.store.store_view')

        store_view = store_view_obj.browse(
            cursor, user, context.get('active_id')
        )

        sales = store_view_obj.import_orders_from_store_view(
            cursor, user, store_view, context
        )

        return self.open_sales(cursor, user, map(int, sales), context)

    def open_sales(self, cursor, user, sale_ids, context):
        """
        Open view for sales imported from the magento store view

        :param cursor: Database cursor
        :param user: ID of current user
        :param sale_ids: List of sale ids
        :param context: Application context
        :return: Tree view for sales
        """
        ir_model_data = self.pool.get('ir.model.data')

        tree_res = ir_model_data.get_object_reference(
            cursor, user, 'sale', 'view_order_tree'
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Magento Sale Orders'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', sale_ids)]
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: