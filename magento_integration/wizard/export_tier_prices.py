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

class ExportTierPrices(osv.TransientModel):
    _name = 'magento.store.export_tier_prices'
    _description = 'Export Tier Prices'

    def export_tier_prices(self, cursor, user, ids, context):
        """
        Export product tier prices to magento for the current store

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        :return: View for products
        """
        store_obj = self.pool.get('magento.website.store')

        store = store_obj.browse(
            cursor, user, context['active_id'], context
        )

        context.update({
            'magento_store': context['active_id'],
        })

        products = store_obj.export_tier_prices_to_magento(
            cursor, user, store, context
        )

        return self.open_products(cursor, user, map(int, products), context)

    def open_products(self, cursor, user, product_ids, context):
        """
        Open view for products for which tier prices have been exported

        :param cursor: Database cursor
        :param user: ID of current user
        :param product_ids: List of product ids
        :param context: Application context
        :return: Tree view for products
        """
        ir_model_data = self.pool.get('ir.model.data')

        tree_res = ir_model_data.get_object_reference(
            cursor, user, 'product', 'product_product_tree_view'
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Products with tier prices exported to Magento'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', product_ids)]
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: