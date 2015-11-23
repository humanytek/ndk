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

import openerp
from magento.catalog import Category, Product
from openerp.osv import osv, fields
from openerp.tools.translate import _

import threading
import logging
import math


class ImportCatalog(osv.TransientModel):
    _name = 'magento.instance.import_catalog'
    _description = 'Import Catalog'
    
    _columns = {
                'import_images': fields.boolean('Import Images?'),
                }

    def import_catalog(self, cursor, user, ids, context):
        """
        Import the product categories and products

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        """
        Pool = self.pool
        website_obj = Pool.get('magento.instance.website')

        website_id = context.get('active_id')
        t = threading.Thread(target=self.import_category_tree,
                             args = (cursor, user, website_id, context, True))
        t.daemon = True
        t.start()
        return True#self.open_categories(cursor, user, ids, category_ids, context)

    def import_category_tree(self, cursor, user, website_id, context=None, use_local_cr=False):
        """
        Imports category tree

        :param cursor: Database cursor
        :param user: ID of current user
        :param website: Browse record of website
        :param context: Application context
        """
        local_cr = cursor
        if use_local_cr:
            db = openerp.sql_db.db_connect(cursor.dbname)
            local_cr = db.cursor()
            
        category_obj = self.pool.get('product.category')
        website_obj = self.pool.get('magento.instance.website')
        website = website_obj.browse(local_cr, user, website_id, context)

        instance = website.instance
        context.update({
            'magento_instance': instance.id
        })

        with Category(
            instance.url, instance.api_user, instance.api_key
        ) as category_api:
            category_tree = category_api.tree(website.magento_root_category_id)

            categ_ids = category_obj.create_tree_using_magento_data(
                local_cr, user, category_tree, context
            )
            
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
            
        return categ_ids
    
    def _import_products(self, cr, uid, ids, website_id, context=None, use_local_cr=False
                         ):
        if context is None:
            context = {}
#         
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
            
        website_obj = self.pool.get('magento.instance.website')
        product_obj = self.pool.get('product.product')
        prod_website_obj = self.pool.get('magento.website.product')
        
        website = website_obj.browse(local_cr, uid, website_id, context)
        instance = website.instance
        _logger = logging.getLogger('Importing Products to OpenERP')
        
        with Product(
            instance.url, instance.api_user, instance.api_key
        ) as product_api:
            mag_products = []
            products = []
            imported_magento_ids = []
            # Products are linked to websites. But the magento api filters
            # the products based on store views. The products available on
            # website are always available on all of its store views.
            # So we get one store view for each website in current instance.
            context.update({
                'magento_website': website.id,
                'magento_instance': website.instance.id,
            })
            prod_website_ids = prod_website_obj.search(local_cr, uid, [('website','=',website_id)], context=context)
            prod_magento_browse = prod_website_obj.browse(local_cr, uid, prod_website_ids, context=context)
            prod_magento_ids = [x.magento_id for x in prod_magento_browse]
            
            str_prod_magento_ids = [str(x) for x in prod_magento_ids]
            
            filters = {
                      'status': {'=': '1'}
                      }
            if str_prod_magento_ids:
                filters.update({
                                'product_id': {'nin': str_prod_magento_ids},
                                })
            
            mag_products.extend(
                product_api.list(filters=filters,
                    store_view=website.stores[0].store_views[0].magento_id
                )
            )
            
            import_images = False
            if self.browse(local_cr, uid, ids and ids[0], context=context).import_images:
                import_images = True
            count = 1
            
            mag_products_total_length = len(mag_products)
            
            # splitting the mag_products array in subarrays to avoid memory leaks in case of massive processing
            l = 200
            f = lambda v, l: [v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))]
            split_mag_products = f(mag_products, l)
            
            for mag_products in split_mag_products:
                for mag_product in mag_products:
                    if int(mag_product['product_id']) not in prod_magento_ids:
                        _logger.info('Importing %s - %s/%s' % (mag_product['name'],count,mag_products_total_length))
                        oe_product_id = product_obj.find_or_create_using_magento_id(
                                local_cr, uid, mag_product['product_id'], context,
                            )
                        products.append(oe_product_id)
                        if import_images:
                            product_obj.import_imgage_from_magento(local_cr, uid, mag_product['product_id'], oe_product_id, context)
                        imported_magento_ids.append(int(mag_product['product_id']))
                        count += 1
        
        self.pool.get('magento.instance.update_catalog').update_products(local_cr, uid, website_id, imported_magento_ids, context)
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
        
        return products

    def import_products(self, cursor, user, ids, context):
        """
        Imports products for current instance

        :param cursor: Database cursor
        :param user: ID of current user
        :param website: Browse record of website
        :param context: Application context
        :return: List of product IDs
        """
        website_id = context.get('active_id')
        
        t = threading.Thread(target=self._import_products,
                             args = (cursor, user, ids, website_id, context, True))
        t.daemon = True
        t.start()
        return True#self.open_products(cursor, user, ids, map(int, products), context)
    
    def import_and_update_products(self, cursor, user, ids, context=None):
        update_catelog_obj = self.pool.get('magento.instance.update_catalog')
        
        website_id = context.get('active_id')
        
        t = threading.Thread(target=self._import_products,
                             args = (cursor, user, ids, website_id, context, True))
        t.daemon = True
        t.start()
        
        return True

    def open_products(self, cursor, user, ids, product_ids, context):
        """
        Opens view for products for current instance

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param product_ids: List or product IDs
        :param context: Application context
        :return: View for products
        """
        ir_model_data = self.pool.get('ir.model.data')

        tree_res = ir_model_data.get_object_reference(
            cursor, user, 'product', 'product_product_tree_view'
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Magento Instance Products'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'product.product',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', product_ids)]
        }
        
    def open_categories(self, cursor, user, ids, category_ids, context):
        """
        Opens view for categories for current instance
        
        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param category_ids: List or category IDs
        :param context: Application context
        :return: View for products
        """
        ir_model_data = self.pool.get('ir.model.data')

        tree_res = ir_model_data.get_object_reference(
            cursor, user, 'product', 'product_category_list_view'
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Magento Instance Product Categories'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'product.category',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', category_ids)]
        }

ImportCatalog()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: