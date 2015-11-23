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
from openerp.osv import osv, fields
from openerp.tools.translate import _
from pychart import category_coord

import magento
import threading
import logging

class ExportCategory(osv.TransientModel):
    "Export Product Category"
    _name = 'magento.instance.website.export_category'
    _description = 'Export Category'
    
    def _get_parent_categ_id(self, category):
        if category.parent_id:
            if category.parent_id.magento_ids:
                return category.parent_id.magento_ids[0].magento_id
            else:
                return False
        else:
            return False
        
    def _export_category(self, cr, uid, website_id, context=None, use_local_cr=False):
        if context is None:
            context = {}
            
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
        
        website_obj = self.pool.get('magento.instance.website')
        categ_obj = self.pool.get('product.category')
        mag_instance_prod_categ_obj = self.pool.get('magento.instance.product_category')
        
        website = website_obj.browse(local_cr, uid, website_id, context)
        
        instance = website.instance
        
        data = {
                'include_in_menu': True,
                'default_sort_by': 'name',
                'available_sort_by': ['name', 'price'],
                }
        
        magento_root_categ_id = website.magento_root_category_id
        
        ctx = context.copy()
        ctx.update({
                    'active_test': False,
                    })
        
        categs_to_create = categ_obj.search(local_cr, uid, [('parent_id','!=', False),('magento_ids','=',None),
                                                     ('exported_to_magento','=',True)], context=ctx)
        with magento.Category(instance.url, instance.api_user, instance.api_key) as category_api:
            for categ_id in categs_to_create:
                categ_browse = categ_obj.browse(local_cr, uid, categ_id, context=context)
                data.update({
                             'name': categ_browse.name,
                             'is_active': categ_browse.active,
                             })
                magento_parent_categ_id = self._get_parent_categ_id(categ_browse) or magento_root_categ_id
                magento_categ_id = category_api.create(magento_parent_categ_id, data, store_view=None)
                mag_instance_prod_categ_obj.create(local_cr, uid, {
                                                            'category': categ_id,
                                                            'magento_id': magento_categ_id,
                                                            'instance': instance.id,
                                                            })
         
        categs_to_update = categ_obj.search(local_cr, uid, [('parent_id','!=', False),('magento_ids','!=',None),
                                                     ('exported_to_magento','=',True)], context=ctx)
        categ_browse = categ_obj.browse(local_cr, uid, categs_to_update, context=context)
         
        with magento.Category(instance.url, instance.api_user, instance.api_key) as category_api:
            i = 0
            for categ_id in categs_to_update:
                current_browse = categ_browse[i]
                ext_categ_id = current_browse.magento_ids[0].magento_id
                data.update({
                             'name': current_browse.name,
                             'is_active': current_browse.active,
                             })
                i += 1
                try:
                    category_api.move(ext_categ_id, self._get_parent_categ_id(current_browse) or magento_root_categ_id, after_id=None)
                    category_api.update(ext_categ_id, data, store_view=None)
                except Exception:
                    pass
        
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
            
        return True
    
    def export_category(self, cr, uid, ids, context=None):
        
        website_id = context.get('active_id')
        
        t = threading.Thread(target=self._export_category,
                             args=(cr, uid, website_id, context, True))
        t.daemon = True
        t.start()

        return True
    
ExportCategory()

class ExportCatalog(osv.TransientModel):
    "Export Catalog"
    _name = 'magento.instance.website.export_catalog'
    _description = 'Export Catalog'

    def get_attribute_sets(self, cursor, user, context=None):
        """Get the list of attribute sets from magento for the current website's
        instance

        :param cursor: Database cursor
        :param user: ID of current user
        :param context: Application context
        :return: Tuple of attribute sets where each tuple consists of (ID, Name)
        """
        website_obj = self.pool.get('magento.instance.website')

        if not context.get('active_id'):
            return []

        website = website_obj.browse(
            cursor, user, context['active_id'], context
        )
        instance = website.instance

        with magento.ProductAttributeSet(
            instance.url, instance.api_user, instance.api_key
        ) as attribute_set_api:
            attribute_sets = attribute_set_api.list()

        return [(
            attribute_set['set_id'], attribute_set['name']
        ) for attribute_set in attribute_sets]
        
    def _get_default_attribute_set(self, cursor, user, context=None):
        website_obj = self.pool.get('magento.instance.website')

        if not context.get('active_id'):
            return False
        website = website_obj.browse(
            cursor, user, context['active_id'], context
        )
        instance = website.instance
        
        with magento.ProductAttributeSet(
            instance.url, instance.api_user, instance.api_key
        ) as attribute_set_api:
            attribute_sets = attribute_set_api.list()
            
        if attribute_sets:
            return attribute_sets[0]['set_id']
        
        return False

    _columns = dict(
        category=fields.many2many(
            'product.category', 'website_category_rel', 'website', 'category', 'Magento Category',
            domain=[('magento_ids', '!=', None)],
        ),
        select_all_categ = fields.boolean('Select All Categories'),
        select_all_products = fields.boolean('Select All Products'),
        products=fields.many2many(
            'product.product', 'website_product_rel', 'website', 'product',
            'Products', required=True, domain=[('magento_ids', '=', None)],
        ),
        attribute_set=fields.selection(
            get_attribute_sets, 'Attribute Set', required=True,
        ),
        export_images=fields.boolean(
            'Export Images?'
        ),
        not_updated_products=fields.text('Product Cannot be exported'),
    )
    
    _defaults = {
                 'attribute_set': _get_default_attribute_set,
                 }
    
    def onchange_category(self, cr, uid, ids, categories, select_all_products, context=None):
        res = {}
        product_pool = self.pool.get('product.product')
        category_ids = categories and categories[0][2] or []
        product_ids = product_pool.search(cr, uid, [('categ_id', 'in', category_ids), ('magento_ids', '=', None), \
                                                         ('default_code', '!=', False)], context=context)
        not_updated_product_ids = product_pool.search(cr, uid, [('categ_id', 'in', category_ids), ('magento_ids','=', None), \
                                                                    ('default_code', '=', False)], context=context)
        not_updated_products = product_pool.browse(cr, uid, not_updated_product_ids, context=context)
        name_list = [x.name for x in not_updated_products]
        if select_all_products:
            res.update({
                        'products': [(6, 0, product_ids)],
                        'not_updated_products': ', '.join(name_list),
                        })
        else:
            res.update({
                        'products': [(6, 0, [])],
                        'not_updated_products': '',
                        })
        if not category_ids:
            res.update({
                        'select_all_products': False,
                        })
        return {'value': res}
    
    def select_all_category(self, cr, uid, ids, select_all_categ, select_all_products, categories, context=None):
        res = {}
        product_pool = self.pool.get('product.product')
        category_pool = self.pool.get('product.category')
        categ_ids = []
        if select_all_categ:
            categ_ids = category_pool.search(cr, uid, [('magento_ids','!=', None)], context=context)
            res.update({
                        'category': [(6, 0, categ_ids)],
                        })
        elif not select_all_categ:
            categ_ids = categories and categories[0][2] or []
        if not select_all_categ:
            res.update({
                        'category': [(6, 0, [])],
                        'products': [(6, 0, [])],
                        'not_updated_products': False,
                        })
        if categ_ids:
            if select_all_products:
                product_ids = product_pool.search(cr, uid, [('categ_id', 'in', categ_ids), ('magento_ids','=', None), \
                                                            ('default_code', '!=', False)], context=context)
                not_updated_product_ids = product_pool.search(cr, uid, [('categ_id', 'in', categ_ids), ('magento_ids','=', None), \
                                                                        ('default_code', '=', False)], context=context)
                not_updated_products = product_pool.browse(cr, uid, not_updated_product_ids, context=context)
                name_list = [x.name for x in not_updated_products]
                res.update({
                            'products': [(6, 0, product_ids)],
                            'not_updated_products': ', '.join(name_list),
                            })
        else:
            res.update({
                        'category': [(6, 0, [])],
                        'products': [(6, 0, [])],
                        'not_updated_products': False,
                        })
            
        return {'value': res}
    
    def select_all_products(self, cr, uid, ids, select_all_products, categories, context=None):
        res = {}
        category_ids = categories and categories[0][2] or []
        if not category_ids:
            raise osv.except_osv(_('Warning!'),_('Please select at least one category to export'))
        
        product_pool = self.pool.get('product.product')
        product_ids = []
            
        if category_ids and select_all_products:
            products_ids = product_pool.search(cr, uid, [('magento_ids', '=', None), ('categ_id', 'in', category_ids), \
                                                                             ('default_code', '!=', False)], context=context)
            not_updated_product_ids = product_pool.search(cr, uid, [('magento_ids', '=', None), ('categ_id', 'in', category_ids), \
                                                                    ('default_code', '=', False)], context=context)
            not_updated_products = product_pool.browse(cr, uid, not_updated_product_ids, context=context)
            name_list = [x.name for x in not_updated_products]
            res.update({
                        'products': [(6, 0, products_ids)],
                        'not_updated_products': ', '.join(name_list),
                        })
        else:
            res.update({
                        'products': [(6, 0, [])],
                        'not_updated_products': False,
                        })
        return {'value': res}
    
    def update_and_export_products_openerp_to_magento(self, cursor, user, ids, context=None):
        
        product_obj = self.pool.get('product.product')
        website_id = context.get('active_id')
        
        ctx = context.copy()
        ctx.update({
                    'search_all_products': True,
                    })
        t = threading.Thread(target=self._export_catalog,
                             args = (cursor, user, ids, website_id, ctx, True))
        t.daemon = True
        t.start()
        
        return True
    
    def _export_catalog(self, cr, uid, ids, website_id, context=None, use_local_cr=False):
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
        
        if context is None:
            context = {}
        
        website_obj = self.pool.get('magento.instance.website')
        product_obj = self.pool.get('product.product')
        
        website = website_obj.browse(local_cr, uid, website_id, context)
        record = self.browse(local_cr, uid, ids[0], context=context)
        _logger = logging.getLogger('Exporting Products... ')

        context.update({
            'magento_website': website.id,
            'magento_attribute_set': record.attribute_set,
        })
        exported_product_ids = []
        export_images = False
        if self.browse(local_cr, uid, ids and ids[0], context=context).export_images:
            export_images = True
        products = record.products
        
        if context.get('search_all_products', False):
            product_ids = product_obj.search(local_cr, uid, [('magento_ids','=', None), ('default_code','!=', False)], context=context)
            products = product_obj.browse(local_cr, uid, product_ids, context=context)
        
        count = 1
        for product in products:
            _logger.info('%s - %s/%s' % (product.name, count, len(products)))
            mag_ext_id = product_obj.export_to_magento(
                local_cr, uid, product, product.categ_id, context=context
            )
            exported_product_ids.append(product.id)
            if export_images:
                product_obj.export_image_to_magento(local_cr, uid, product, mag_ext_id, context=context)
            count += 1
            
        product_obj.update_products_to_magento(local_cr, uid, exported_product_ids, website_id, context)
        
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
            
        return True

    def export_catalog(self, cursor, user, ids, context):
        """
        Export the products selected to the selected category for this website

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        """
        website_id = context.get('active_id')
        
        t = threading.Thread(target=self._export_catalog,
                             args = (cursor, user, ids, website_id, context, True))
        t.daemon = True
        t.start()
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cursor, user, 'magento_integration', 'instance_website_form_view')
        view_id = view_ref and view_ref[1] or False
        
        return {
           'type': 'ir.actions.act_window',
           'name': _('Website'),
           'res_model': 'magento.instance.website',
           'view_type': 'form',
           'res_id': website_id,
           'view_id': view_id,
           'view_mode': 'form',
           'target': 'current',
           'nodestroy': True,
           }

    def open_products(self, cursor, user, ids, product_ids, context):
        """
        Opens view for products exported to current website

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param product_ids: List or product IDs
        :param context: Application context
        :return: View for products
        """
        ir_model_data = self.pool.get('ir.model.data')

        model, tree_id = ir_model_data.get_object_reference(
            cursor, user, 'product', 'product_product_tree_view'
        )

        return {
            'name': _('Products exported to magento'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'product.product',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', product_ids)]
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: