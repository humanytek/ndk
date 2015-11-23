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

import magento
import mimetypes
import urllib2
import datetime

import openerp
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
import math

_logger = logging.getLogger(__name__)

class Category(osv.Model):
    _inherit = 'product.category'
    _description = 'Product Category' 

    _columns = dict(
        magento_ids=fields.one2many(
            'magento.instance.product_category', 'category',
            string='Magento IDs', readonly=True,
        ),
        active=fields.boolean('Active'),
        exported_to_magento=fields.boolean('Exported to Magento?'),
    )
    
    _defaults = {
                 'active': True,
                'exported_to_magento': True,
                 }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('parent_id', False) and not context.get('importing'):
            exported = self.browse(cr, uid, vals['parent_id'], context=context).exported_to_magento
            vals.update({
                         'exported_to_magento': exported,
                         })
        return super(Category, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
            
        if 'exported_to_magento' in vals and not context.get('update'):
            ctx = context.copy()
            ctx.update({'update': True})
            categ_ids = self.search(cr, uid, [('parent_id','in', ids)], context=context)
            if vals['exported_to_magento']:
                self.write(cr, uid, categ_ids, {
                                          'exported_to_magento': True,
                                          }, ctx)
            else:
                self.write(cr, uid, categ_ids, {
                                          'exported_to_magento': False,
                                          }, ctx)
                
        return super(Category, self).write(cr, uid, ids, vals, context=context)

    def create_tree_using_magento_data(
        self, cursor, user, category_tree, context
    ):
        """Create the categories from the category tree

        :param cursor: Database cursor
        :param user: ID of current user
        :param category_tree: Category Tree from magento
        :param context: Application context
        """
        # Create the root
        print "create_tree_using_magento_data"
        categ_ids = []
        root_categ = self.find_or_create_using_magento_data(
            cursor, user, category_tree, context=context
        )
        if root_categ:
            categ_ids.append(root_categ.id)
        for child in category_tree['children']:
            categ = self.find_or_create_using_magento_data(
                cursor, user, child, parent=root_categ.id, context=context
            )
            categ_ids.append(categ.id)
            if child['children']:
                self.create_tree_using_magento_data(
                    cursor, user, child, context
                )
        return categ_ids

    def find_or_create_using_magento_data(
        self, cursor, user, category_data, parent=None, context=None
    ):
        """Find or Create category using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param category_data: Category Data from magento
        :param parent: openerp ID of parent if present else None
        :param context: Application context
        :returns: Browse record of category found/created
        """
        print "find_or_create_using_magento_data"
        category = self.find_using_magento_data(
            cursor, user, category_data, context
        )
        if not category:
            category = self.create_using_magento_data(
                cursor, user, category_data, parent, context
            )

        return category
    
    def find_or_create_using_magento_id(
        self, cursor, user, magento_id, parent=None, context=None
    ):
        """Find or Create category using magento ID of category

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Category ID from magento
        :param parent: openerp ID of parent if present else None
        :param context: Application context
        :returns: Browse record of category found/created
        """
        instance_obj = self.pool.get('magento.instance')

        category = self.find_using_magento_id(
            cursor, user, magento_id, context
        )
        if not category:
            instance = instance_obj.browse(
                cursor, user, context['magento_instance'], context=context
            )

            with magento.Category(
                instance.url, instance.api_user, instance.api_key
            ) as category_api:
                category_data = category_api.info(magento_id)

            category = self.create_using_magento_data(
                cursor, user, category_data, parent, context
            )

        return category

    def find_using_magento_data(
        self, cursor, user, category_data, context=None
    ):
        """Find category using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param category_data: Category Data from magento
        :param context: Application context
        :returns: Browse record of category found or None
        """
        magento_category_obj = self.pool.get('magento.instance.product_category')
        record_ids = magento_category_obj.search(cursor, user, [
            ('magento_id', '=', int(category_data['category_id'])),
            ('instance', '=', context['magento_instance'])
        ], context=context)
        return record_ids and magento_category_obj.browse(
            cursor, user, record_ids[0], context=context
        ).category or None

    def find_using_magento_id(
        self, cursor, user, magento_id, context=None
    ):
        """Find category using magento id or category

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Category ID from magento
        :param context: Application context
        :returns: Browse record of category found or None
        """
        magento_category_obj = self.pool.get('magento.instance.product_category')
        website_obj = self.pool.get('magento.instance.website')
        instance = website_obj.browse(cursor, user, context['magento_website'], context=context)
        
        record_ids = magento_category_obj.search(cursor, user, [
            ('magento_id', '=', magento_id),
            ('instance', '=', instance.id)
        ], context=context)
        return record_ids and magento_category_obj.browse(
            cursor, user, record_ids[0], context=context
        ).category or None

    def create_using_magento_data(
        self, cursor, user, category_data, parent=None, context=None
    ):
        """Create category using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param category_data: Category Data from magento
        :param parent: openerp ID of parent if present else None
        :param context: Application context
        :returns: Browse record of category created
        """
        ctx = context.copy()
        ctx.update({'importing': True})
        
        category_id = self.create(cursor, user, {
            'name': category_data['name'],
            'parent_id': parent,
            'exported_to_magento': True,
            'magento_ids': [(0, 0, {
                'magento_id': int(category_data['category_id']),
                'instance': context['magento_instance'],
            })]
        }, context=ctx)

        return self.browse(cursor, user, category_id, context=context)
    
    def update_category_in_openerp(self, cr, uid, category_tree, instance, context=None):
        if context is None:
            context = {}
        
        magento_instance_categ_pool = self.pool.get('magento.instance.product_category')
        categ_ids = self.search(cr, uid, [('name','=ilike', category_tree['name'])], context=context)
        if categ_ids:
            categ_id = categ_ids[0]
            magento_instance_categ_pool.create(cr, uid, {
                                                         'magento_id': category_tree['category_id'],
                                                         'instance': instance.id,
                                                         'category': categ_id,
                                                         })
        for child in category_tree['children']:
            self.update_category_in_openerp(cr, uid, child, instance, context)
        return True
    
    def link_magento_and_openerp_categories(self, cr, uid, website_id, context=None, use_local_cr=False):
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
            
        if context is None:
            context = {}
            
        website_obj = self.pool.get('magento.instance.website')
        website = website_obj.browse(local_cr, uid, website_id, context)
        
        instance = website.instance
        
        with magento.Category(instance.url, instance.api_user, instance.api_key) as category_api:
            category_tree = category_api.tree(parent_id=website.magento_root_category_id, store_view=None)
        
        self.update_category_in_openerp(local_cr, uid, category_tree, instance, context=context)
        
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
        
        return True

class MagentoInstanceCategory(osv.Model):
    """Magento Instance - Product category store

    This model keeps a record of a category's association with an instance and
    the ID of category on that instance
    """
    _name = 'magento.instance.product_category'
    _description = 'Magento Instance - Product category store'

    _columns = dict(
        magento_id=fields.integer(
            'Magento ID', readonly=True, required=True, select=True,
        ),
        instance=fields.many2one(
            'magento.instance', 'Magento Instance', readonly=True,
            select=True, required=True
        ),
        category=fields.many2one(
            'product.category', 'Product Category', readonly=True,
            required=True, select=True
        )
    )

    _sql_constraints = [
        (
            'magento_id_instance_unique',
            'unique(magento_id, instance)',
            'Each category in an instance must be unique!'
        ),
    ]


class Product(osv.Model):
    _inherit = 'product.product'
    _description = 'Product' 

    _columns = dict(
        magento_product_type=fields.selection([
            ('simple', 'Simple'),
            ('configurable', 'Configurable'),
            ('grouped', 'Grouped'),
            ('bundle', 'Bundle'),
            ('virtual', 'Virtual'),
            ('downloadable', 'Downloadable'),
        ], 'Magento Product type', readonly=True),
        magento_ids=fields.one2many(
            'magento.website.product', 'product',
            string='Magento IDs', readonly=True,
        ),
        price_tiers=fields.one2many(
            'product.price_tier', 'product', string='Price Tiers'
        ),
        image_ids=fields.one2many(
            'product.images', 'product_id', 'Product Images'
        ),
        short_description=fields.char('Short Description', size=64),
        active_in_magento=fields.boolean('Active in Magento'),
    )
    
    _defaults = {
                 'active_in_magento': True,
                 }
    
    def import_imgage_from_magento(self, cursor, user, magento_id, oe_product_id, context):
        website_obj = self.pool.get('magento.instance.website')
        product_image_obj = self.pool.get('product.images')
        product_obj = self.pool.get('product.product')
        website = website_obj.browse(
                cursor, user, context['magento_website'], context=context
            )
        instance = website.instance
        with magento.ProductImages(instance.url, instance.api_user, instance.api_key) as image_api:
            images = []
            for image in image_api.list(magento_id, store_view=None):
                url = image['url']
                images.append(url)
                try:
                    product_image_obj.create(cursor, user, {
                                                            'product_id': oe_product_id.id,
                                                            'name': url.split('/')[-1],
                                                            'filename': url,
                                                            'comments': url.split('/')[-1].split('.')[0],
                                                          })
                except Exception, e:
                    pass
                
            if images:
                title_image = False
                try:
                    title_image =  urllib2.urlopen(images[0]).read().encode("base64").replace("\n","")
                except Exception,e:
                    pass
                if title_image:
                    product_obj.write(cursor, user, [oe_product_id.id], {
                                                                        'image_medium': title_image,
                                                                        })
        
        return True
    
    def export_image_to_magento(self, cursor, user, product, product_extid, context=None):
        
        website_obj = self.pool.get('magento.instance.website')
        website_product_obj = self.pool.get('magento.website.product')
        
        website = website_obj.browse(
                cursor, user, context['magento_website'], context=context
            )
        instance = website.instance
        if product.image:
            thumbnail_image_data = {
                                    'file': {
                                             'name': product.name,
                                             'content': product.image,
                                             'mime': 'image/jpeg',
                                             }
                                    }
            with magento.Product(instance.url, instance.api_user, instance.api_key) as image_api:
                try:
                    image_api.call('catalog_product_attribute_media.create', [product_extid, thumbnail_image_data, False, 'id'])
                except Exception, e:
                    raise osv.except_osv(_('Warning!'), _(str(e)))
        for each in product.image_ids:
            data = {
                    'file':{
                        'name':each.name,
                        'content': each.preview,
                        'mime': each.link and each.filename and mimetypes.guess_type(each.filename)[0] \
#                                 or each.extention and mimetypes.guess_type(each.name + each.extention)[0] \
                                or 'image/jpeg',
                        }
                    }
            
            with magento.Product(
                instance.url, instance.api_user, instance.api_key
            ) as product_api:
                try:
                    product_api.call('catalog_product_attribute_media.create', [product_extid, data, False, 'id'])
                except Exception, e:
                    raise osv.except_osv(_('Warning!'), _(str(e)))
        return True

    def find_or_create_using_magento_id(
        self, cursor, user, magento_id, context
    ):
        """
        Find or create product using magento_id

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Product ID from magento
        :param context: Application context
        :returns: Browse record of product found/created
        """
        website_obj = self.pool.get('magento.instance.website')

        product = self.find_using_magento_id(
            cursor, user, magento_id, context
        )
        if not product:
            # If product is not found, get the info from magento and delegate
            # to create_using_magento_data
            website = website_obj.browse(
                cursor, user, context['magento_website'], context=context
            )

            instance = website.instance
            with magento.Product(
                instance.url, instance.api_user, instance.api_key
            ) as product_api:
                try:
                    product_data = product_api.info(magento_id)
                except Exception, e:
                    raise osv.except_osv(_('Warning!'), _(str(e)))

            product = self.create_using_magento_data(
                cursor, user, product_data, context
            )

        return product

    def find_using_magento_id(self, cursor, user, magento_id, context):
        """
        Finds product using magento id

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Product ID from magento
        :param context: Application context
        :returns: Browse record of product found
        """
        magento_product_obj = self.pool.get('magento.website.product')

        record_ids = magento_product_obj.search(
            cursor, user, [
                ('magento_id', '=', magento_id),
                ('website', '=', context['magento_website'])
            ], context=context
        )

        return record_ids and magento_product_obj.browse(
            cursor, user, record_ids[0], context=context
        ).product or None

    def find_or_create_using_magento_data(
        self, cursor, user, product_data, context=None
    ):
        """Find or Create product using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param product_data: Product Data from magento
        :param context: Application context
        :returns: Browse record of product found/created
        """
        product = self.find_using_magento_data(
            cursor, user, product_data, context
        )
        if not product:
            product = self.create_using_magento_data(
                cursor, user, product_data, context
            )

        return product

    def find_using_magento_data(
        self, cursor, user, product_data, context=None
    ):
        """Find product using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param product_data: Category Data from magento
        :param context: Application context
        :returns: Browse record of product found or None
        """
        magento_product_obj = self.pool.get('magento.website.product')
        record_ids = magento_product_obj.search(cursor, user, [
            ('magento_id', '=', int(product_data['product_id'])),
            ('website', '=', context['magento_website'])
        ], context=context)
        return record_ids and magento_product_obj.browse(
            cursor, user, record_ids[0], context=context
        ).product or None

    def update_from_magento(
        self, cursor, user, product, magento_api, website, context=None
    ):
        """Update product using magento ID for that product

        :param cursor: Database cursor
        :param user: ID of current user
        :param product: Browse record of product to be updated
        :param context: Application context
        :returns: Browse record of product updated
        """
        magento_product_obj = self.pool.get('magento.website.product')

        try:        
            with magento_api as product_api:
                magento_product_id, = magento_product_obj.search(
                    cursor, user, [
                        ('product', '=', product.id),
                        ('website', '=', website.id),
                    ], context=context
                )
                magento_product = magento_product_obj.browse(
                    cursor, user, magento_product_id, context=context
                )
                try:
                    product_data = product_api.info(magento_product.magento_id)
                except Exception, e:
                    #Retry update of the same product
                    self.update_from_magento(cursor, user, product, magento_api, website, context)
        except Exception, e: #Retry with a new magento API if the existing one has expired
            instance = website.instance
            magento_api = magento.Product(instance.url, instance.api_user, instance.api_key)
            self.update_from_magento(cursor, user, product, magento_api, website, context)

        return self.update_from_magento_using_data(
            cursor, user, product, product_data, context
        )

    def extract_product_values_from_data(self, product_data):
        """Extract product values from the magento data
        These values are used for creation/updation of product

        :param product_data: Product Data from magento
        :return: Dictionary of values
        """
        return {
            'name': product_data['name'],
            'default_code': product_data['sku'],
            'description': product_data['description'],
            'short_description': product_data['short_description'],
            'list_price': float(
                product_data.get('special_price') or
                product_data.get('price') or 0.00
            ),
            'standard_price': float(product_data.get('price') or 0.00),
        }

    def update_from_magento_using_data(
        self, cursor, user, product, product_data, context=None
    ):
        """Update product using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param product: Browse record of product to be updated
        :param product_data: Product Data from magento
        :param context: Application context
        :returns: Browse record of product updated
        """
        product_values = self.extract_product_values_from_data(product_data)
        self.write(cursor, user, product.id, product_values, context=context)

        # Rebrowse the record
        product = self.browse(cursor, user, product.id, context=context)

        return product

    def create_using_magento_data(
        self, cursor, user, product_data, context=None
    ):
        """Create product using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param product_data: Product Data from magento
        :param context: Application context
        :returns: Browse record of product created
        """
        category_obj = self.pool.get('product.category')
        website_obj = self.pool.get('magento.instance.website')

        # Get only the first category from list of categories
        # If not category is found, put product under unclassified category
        # which is created by default data
        if product_data.get('categories'):
            category_id = category_obj.find_or_create_using_magento_id(
                cursor, user, int(product_data['categories'][0]),
                context=context
            ).id
        else:
            category_id, = category_obj.search(cursor, user, [
                ('name', '=', 'Unclassified Magento Products')
            ], context=context)

        product_values = self.extract_product_values_from_data(product_data)
        product_values.update({
            'categ_id': category_id,
            'uom_id':
                website_obj.get_default_uom(
                    cursor, user, context
                ).id,
            'magento_product_type': product_data['type'],
            'procure_method': 'make_to_order',
            'magento_ids': [(0, 0, {
                'magento_id': int(product_data['product_id']),
                'website': context['magento_website'],
            })]
        })

        if product_data['type'] == 'bundle':
            # Bundles are produced
            product_values['supply_method'] = 'produce'

        product_id = self.create(cursor, user, product_values, context=context)

        return self.browse(cursor, user, product_id, context=context)

    def get_product_values_for_export_to_magento(
        self, product, categories, websites, context
    ):
        """Creates a dictionary of values which have to exported to magento for
        creating a product

        :param product: Browse record of product
        :param categories: List of Browse record of categories
        :param websites: List of Browse record of websites
        :param context: Application context
        """
        return {
            'categories': map(
                lambda mag_categ: mag_categ.magento_id,
                categories[0].magento_ids
            ),
            'websites': map(lambda website: website.magento_id, websites),
            'name': product.name,
            'description': product.description or product.name,
            'short_description': product.short_description or product.description or product.name,
            'status': '1',
            'weight': product.weight_net,
            'visibility': '4',
            'price': product.lst_price,
            'tax_class_id': '1',
        }

    def export_to_magento(self, cursor, user, product, category, context):
        """Export the given `product` to the magento category corresponding to
        the given `category` under the current website in context

        :param cursor: Database cursor
        :param user: ID of current user
        :param product: Browserecord of product to be exported
        :param category: Browserecord of category to which the product has
                         to be exported
        :param context: Application context
        :return: Browserecord of product
        """
        website_obj = self.pool.get('magento.instance.website')
        website_product_obj = self.pool.get('magento.website.product')
        magento_id = False

        if not category.magento_ids:
            raise osv.except_osv(
                _('Invalid Category!'),
                _('Category %s must have a magento category associated') %
                category.complete_name,
            )

        if product.magento_ids:
            raise osv.except_osv(
                _('Invalid Product!'),
                _('Product %s already has a magento product associated') %
                product.name,
            )

        if not product.default_code:
            raise osv.except_osv(
                _('Invalid Product!'),
                _('Product %s has a missing code.') %
                product.name,
            )

        website = website_obj.browse(
            cursor, user, context['magento_website'], context=context
        )
        instance = website.instance

        with magento.Product(
            instance.url, instance.api_user, instance.api_key
        ) as product_api:
            # We create only simple products on magento with the default
            # attribute set
            try:
                magento_id = product_api.call(
                    'ol_catalog_product.create', [
                        'simple',
                        int(context['magento_attribute_set']),
                        product.default_code,
                        self.get_product_values_for_export_to_magento(
                            product, [category], [website], context
                        )
                    ]
                )
            except Exception, e:
                raise osv.except_osv(_('Warning!'), _(str(e)))
            website_product_obj.create(cursor, user, {
                'magento_id': magento_id,
                'website': context['magento_website'],
                'product': product.id,
            }, context=context)
            self.write(cursor, user, product.id, {
                'magento_product_type': 'simple'
            }, context=context)
        return magento_id
    
    def link_magento_and_openerp_products_using_default_code(self, cr, uid, website_id, context=None, use_local_cr=False):
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
            
        if context is None:
            context = {}
        
        prod_website_obj = self.pool.get('magento.website.product')
        website_obj = self.pool.get('magento.instance.website')
        
        website = website_obj.browse(
            local_cr, uid, context['active_id'], context
        )
        instance = website.instance
        
        products_to_link = self.search(local_cr, uid, [('magento_ids','=', None), ('default_code', '!=', False)], context=context)
        
        # splitting the products_to_link array in subarrays to avoid memory leaks in case of massive linking
        l = 200
        f = lambda v, l: [v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))]
        split_products_to_link = f(products_to_link, l)
        
        
        with magento.Product(instance.url, instance.api_user, instance.api_key) as product_api:
            i = 1
            for products in split_products_to_link:
                for product in self.browse(local_cr, uid, products, context=context):
                    filter = {'sku': {'=': product.default_code}}
                    product_list = []
                    try:
                        product_list = product_api.list(filter)
                    except Exception, e:
                        _logger.info(str(e))
                        self.link_magento_and_openerp_products_using_default_code(local_cr, uid, website, context)
                    if product_list:
                        mag_ext_product_id = product_list[0].get('product_id', False)
                        _logger.info("Syncing Product %s %s/%s" % (product.name, i, len(products_to_link)))
                        prod_website_obj.create(local_cr, uid, {
                                                     'product': product.id,
                                                     'magento_id': mag_ext_product_id,
                                                     'website': website_id,
                                                     })
                    else:
                        _logger.info("Fault 101: 'Product not exists.'")
                        continue
                    i += 1
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
            
        return True
    
    def update_products_to_magento(self, cr, uid, exported_product_ids, website_idnum, context, #use_local_cr=True
                                   ):
        if context is None:
            context = {}
            
        local_cr = cr
#         if use_local_cr:
#             db = openerp.sql_db.db_connect(cr.dbname)
#             local_cr = db.cursor()
            
        product_ids = []
        if context.get('product_id', False):#For Updating product from product form view one at a time
            product_ids = [context.get('product_id')]
        
        _logger = logging.getLogger('Update Products OpenERP -> Magento')
            
        website_obj = self.pool.get('magento.instance.website')
        prod_website_obj = self.pool.get('magento.website.product')
        
        website = website_obj.browse(local_cr, uid, website_idnum, context=context)
        
        if not product_ids:
            search_condition = [('magento_ids','!=', None), ('default_code', '!=', False)]
            if website.last_updated_openerp_to_magento:
                search_condition.append(('write_date','>=', website.last_updated_openerp_to_magento))
            product_ids = self.search(local_cr, uid, search_condition, context=context)
            
        product_ids = filter(lambda x: x not in exported_product_ids, product_ids)
        
        instance = website.instance
        product_browse_list = self.browse(local_cr, uid, product_ids, context=context)
        if product_ids:
            with magento.Product(instance.url, instance.api_user, instance.api_key) as product_api:
                i = 0
                for product_id in product_ids:
                    website_ids =  prod_website_obj.search(local_cr, uid, [('product','=',product_id), ('website','=',website.id)], context=context)
                    website_id = website_ids and website_ids[0] or False
                    if website_id:
                        prod_ext_id = prod_website_obj.browse(local_cr, uid, website_id, context=context).magento_id
                        if product_browse_list[i].active_in_magento:
                            status = '1'
                        else:
                            status = '2'
                        data = {
                                'name': product_browse_list[i].name,
                                'description': product_browse_list[i].description or product_browse_list[i].name,
                                'short_description': product_browse_list[i].short_description or product_browse_list[i].description or product_browse_list[i].name,
                                'weight': product_browse_list[i].weight_net,
                                'price': product_browse_list[i].lst_price,
                                'status': status,
                                }
                        _logger.info('Updating %s - %s/%s' % (product_browse_list[i].name,i+1,len(product_ids)))
                        product_api.call('ol_catalog_product.update', [prod_ext_id, data, None])
                    i += 1
        
        website_obj.write(local_cr, uid, [website_idnum], {
                                                           'last_updated_openerp_to_magento': datetime.datetime.now(),
                                                           })
#         if use_local_cr:
#             local_cr.commit()
#             local_cr.close()            
        
        return True
    
class MagentoWebsiteProduct(osv.Model):
    """Magento Website - Product store

    This model keeps a record of a product's association with a website and
    the ID of product on that website
    """
    _name = 'magento.website.product'
    _description = 'Magento Website - Product store'

    _columns = dict(
        magento_id=fields.integer(
            'Magento ID', readonly=True, required=True, select=True,
        ),
        website=fields.many2one(
            'magento.instance.website', 'Magento Website', readonly=True,
            select=True, required=True
        ),
        product=fields.many2one(
            'product.product', 'Product', readonly=True,
            required=True, select=True
        )
    )

    _sql_constraints = [
        (
            'magento_id_website_unique',
            'unique(magento_id, website)',
            'Each product in a website must be unique!'
        ),
    ]

    def update_product_from_magento(self, cursor, user, ids, context):
        """Update the product from magento with the details from magento
        for the current website

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: Record IDs
        :param context: Application context
        """
        product_obj = self.pool.get('product.product')

        for record in self.browse(cursor, user, ids, context=context):
            context.update({
                'magento_website': record.website.id,
            })
            instance = record.website.instance
            magento_api = magento.Product(instance.url, instance.api_user, instance.api_key)
            product_obj.update_from_magento(
                cursor, user, record.product, magento_api, record.website, context
            )

        return {}
    
    def update_product_to_magento(self, cr, uid, ids, context=None):

        product_obj = self.pool.get('product.product')
        
        for record in self.browse(cr, uid, ids, context=context):
            context.update({
                            'product_id': record.product.id,
                            })
            product_obj.update_products_to_magento(cr, uid, record.website.id, context, use_local_cr=False)
            
        return True


class ProductPriceTier(osv.Model):
    """Price Tiers for product

    This model stores the price tiers to be used while sending
    tier prices for a product from OpenERP to Magento.
    """
    _name = 'product.price_tier'
    _description = 'Price Tiers for product'
    _rec_name = 'quantity'

    def get_price(self, cursor, user, ids, name, _, context):
        """Calculate the price of the product for quantity set in record

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: Records IDs
        :param name: Nameo of field
        :param context: Application context
        """
        pricelist_obj = self.pool.get('product.pricelist')
        store_obj = self.pool.get('magento.website.store')

        res = {}

        if not context.get('magento_store'):
            return res

        for tier in self.browse(cursor, user, ids, context=context):
            store = store_obj.browse(
                cursor, user, context['magento_store'], context=context
            )
            res[tier.id] = pricelist_obj.price_get(
                cursor, user, [store.shop.pricelist_id.id], tier.product.id,
                tier.quantity, context={
                    'uom': store.website.default_product_uom.id
                }
            )[store.shop.pricelist_id.id]
        return res

    _columns = dict(
        product=fields.many2one(
            'product.product', 'Product', required=True,
            readonly=True,
        ),
        quantity=fields.float(
            'Quantity', digits_compute=dp.get_precision('Product UoS'),
            required=True
        ),
        price=fields.function(get_price, type='float', string='Price'),
    )

    _sql_constraints = [
        ('product_quantity_unique', 'unique(product, quantity)',
         'Quantity in price tiers must be unique for a product'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: