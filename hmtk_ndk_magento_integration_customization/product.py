# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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

import magento
import openerp
from openerp.osv import fields, osv

from datetime import datetime
class Product(osv.Model):
    _inherit = 'product.product'
    
    _columns = dict(
                    short_description=fields.char('Short Description', size=256),
                )
    
    def update_attributes(self, cursor, user, product, product_data, attribute_set_var, context=None):
        db = openerp.sql_db.db_connect(cursor.dbname)
        local_cr = db.cursor()
        website_obj = self.pool.get('magento.instance.website')
        supplier_info_obj = self.pool.get('product.supplierinfo')
        website = website_obj.browse(
                local_cr, user, context['magento_website'], context=context
            )
        partner_obj = self.pool.get('res.partner')
        instance = website.instance
        product_dict = {}
        with magento.ProductAttribute(instance.url, instance.api_user, instance.api_key) as attribute_api:
                attributes_lists = attribute_api.list(int(attribute_set_var))
                manufacturer = filter(lambda manufacturer:  manufacturer['code']=='manufacturer', attributes_lists)[0]
                manufacturer_options = attribute_api.options(manufacturer['attribute_id'])
                manufacturer_value = filter(lambda manufacturer_value:  manufacturer_value['value']== product_data['manufacturer'], manufacturer_options)
                if manufacturer_value:
                    partner_id = partner_obj.search(local_cr, user, [('name', '=ilike', manufacturer_value[0]['label'])], context=context)
                    if partner_id:
                        quotation_description = self.set_quotation_description(local_cr, user, product_data, attributes_lists, context)
                        if not product.seller_ids:
                            partner_dict = [(0, 0, {
                    'name': int(partner_id[0]),
                    'product_code': product_data['itemno_proveedor'],
                    'min_qty': 0.0,
                    'delay': 1,
                    
                    })]
                            product_dict = {'seller_ids': partner_dict, 'description_purchase': product_data['descripcion_en_ingles'],
                                                     'description_sale': quotation_description, 'model': product_data['modelo']}
                        else:
                            partner_dict = {
                        'name': int(partner_id[0]),
                        'product_code': product_data['itemno_proveedor'],
                        'min_qty': 0.0,
                        'delay': 1,
                        
                        }
                            supplier_info_ids = [supplier_info.id for supplier_info in product.seller_ids]
                            supplier_info_obj.write(local_cr, user, supplier_info_ids, partner_dict, context=context)
                            product_dict = {'description_purchase': product_data['descripcion_en_ingles'],
                                                     'description_sale': quotation_description, 'model': product_data['modelo']}
        local_cr.commit()
        local_cr.close()
        return product_dict
    
    def set_muebles_attributes(self, cursor, user, product_data, attribute_set_var, context=None):
        db = openerp.sql_db.db_connect(cursor.dbname)
        local_cr = db.cursor()
        website_obj = self.pool.get('magento.instance.website')
        supplier_info_obj = self.pool.get('product.supplierinfo')
        website = website_obj.browse(
                local_cr, user, context['magento_website'], context=context
            )
        partner_obj = self.pool.get('res.partner')
        instance = website.instance
        product_dict = {}
        with magento.ProductAttribute(instance.url, instance.api_user, instance.api_key) as attribute_api:
                attributes_lists = attribute_api.list(int(attribute_set_var))
                manufacturer = filter(lambda manufacturer:  manufacturer['code']=='manufacturer', attributes_lists)[0]
                manufacturer_options = attribute_api.options(manufacturer['attribute_id'])
                
                manufacturer_value = filter(lambda manufacturer_value:  manufacturer_value['value']== product_data['manufacturer'], manufacturer_options)
                if manufacturer_value:
                    partner_id = partner_obj.search(local_cr, user, [('name', '=ilike', manufacturer_value[0]['label'])], context=context)
                    dict_supplier =  {} 
                    if partner_id:
                        quotation_description = self.set_quotation_description(local_cr, user, product_data, attributes_lists, context)
                        dict_supplier.update({
                'name': int(partner_id[0]),
                'product_code': product_data['itemno_proveedor'],
                'min_qty': 0.0,
                'delay': 1,
                
                })
                        partner_dict = [(0, 0, dict_supplier)]
                        product_dict = {'seller_ids': partner_dict, 'description_purchase': product_data['descripcion_en_ingles'],
                                                     'description_sale': quotation_description, 'model': product_data['modelo'],}
        local_cr.commit()
        local_cr.close()

        return product_dict
                
    def set_quotation_description(self, cursor, user, product_data, attributes_lists, context=None):
        db = openerp.sql_db.db_connect(cursor.dbname)
        local_cr = db.cursor()
        website_obj = self.pool.get('magento.instance.website')
        website = website_obj.browse(
                local_cr, user, context['magento_website'], context=context
            )
        instance = website.instance
        quotation_description = ''
        with magento.ProductAttribute(instance.url, instance.api_user, instance.api_key) as attribute_api:
            if 'garantia' in product_data:
                if product_data['garantia']:
                    quotation_description += product_data['garantia'] + ', '
            if 'tamano' in product_data:
                if product_data['tamano'] :
                    tamano = filter(lambda tamano:  tamano['code']=='tamano', attributes_lists)[0]
                    tamano_options = attribute_api.options(tamano['attribute_id'])
                    tamano_value = filter(lambda tamano_dict:  tamano_dict['value']== product_data['tamano'], tamano_options)[0]
                    if tamano_value: 
                        quotation_description += tamano_value['label'] + ', '
            if 'color' in product_data:
                if product_data['color']:
                    color = filter(lambda set:  set['code']=='color', attributes_lists)[0]
                    color_options = attribute_api.options(color['attribute_id'])
                    color_value = filter(lambda color_dict:  color_dict['value']== product_data['color'], color_options)[0]
                    if color_value: 
                        quotation_description += color_value['label'] + ', '
            if 'medidas' in product_data:
                if product_data['medidas']:
                    quotation_description += product_data['medidas']
        local_cr.commit()
        local_cr.close()            
        return quotation_description
        

    
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
        db = openerp.sql_db.db_connect(cursor.dbname)
        local_cr = db.cursor()
        category_obj = self.pool.get('product.category')
        website_obj = self.pool.get('magento.instance.website')
        
        website = website_obj.browse(
                local_cr, user, context['magento_website'], context=context
            )
        instance = website.instance
        # Get only the first category from list of categories
        # If not category is found, put product under unclassified category
        # which is created by default data
        other_categ_ids = []
        if product_data.get('categories'):
            category_id = category_obj.find_or_create_using_magento_id(
                cursor, user, int(product_data['categories'][0]),
                context=context
            ).id
            #adding other categorties into the manytomany field
            categ_to_remove = product_data['categories'][0]
            other_magento_categ_list = product_data.get('categories')
            if other_magento_categ_list:
                for other_magento_categ in other_magento_categ_list:
                    if other_magento_categ <> categ_to_remove:
                        categ_to_append = category_obj.find_or_create_using_magento_id(
                    cursor, user, int(other_magento_categ),
                    context=context
                ) and category_obj.find_or_create_using_magento_id(
                    cursor, user, int(other_magento_categ),
                    context=context
                ).id or False
                        if categ_to_append:
                            other_categ_ids.append(categ_to_append)
                    
                    
        else:
            category_id, = category_obj.search(cursor, user, [
                ('name', '=', 'Unclassified Magento Products')
            ], context=context)

        product_values = self.extract_product_values_from_data(product_data)
        #Add the other category ids under many2many field for other category fields
        if other_categ_ids:
            product_values.update({'other_product_category_ids': [(6, 0, other_categ_ids)]})
            
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

        # Additional functionality
        product_attribute_dict = {}
        with magento.ProductAttributeSet(instance.url, instance.api_user, instance.api_key) as attribute_set_api:
            default_attribute_set = filter(lambda attribute_set:  attribute_set['name']=='Default', attribute_set_api.list())[0]
            if not int(default_attribute_set['set_id']) == int(product_data['set']):
                product_attribute_dict = self.set_muebles_attributes(cursor, user, product_data, int(product_data['set']), context=context)
        if product_attribute_dict:
            product_values.update(product_attribute_dict)
        product_id = self.create(local_cr, user, product_values, context=context)
        local_cr.commit()
        local_cr.close()
        return self.browse(cursor, user, product_id, context=context)
    
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
        db = openerp.sql_db.db_connect(cursor.dbname)
        local_cr = db.cursor()
        website_obj = self.pool.get('magento.instance.website')
        category_obj = self.pool.get('product.category')
        seller_info = self.pool.get('product.supplierinfo')
        prod_website_obj = self.pool.get('magento.website.product')
        website = website_obj.browse(
                local_cr, user, context['magento_website'], context=context
            )
        instance = website.instance
        product_values = self.extract_product_values_from_data(product_data)
        other_categ_ids = []
        #Other Categories
        if product_data.get('categories'):
            category_id = category_obj.find_or_create_using_magento_id(
                cursor, user, int(product_data['categories'][0]),
                context=context
            ).id
            #adding other categorties into the manytomany field
#             categ_to_remove = product_data['categories'][0]
            other_magento_categ_list = product_data.get('categories')
#             other_magento_categ_list = other_magento_categ_list.remove(categ_to_remove)
            if other_magento_categ_list:
                for other_magento_categ in other_magento_categ_list:
                    categ_to_append = category_obj.find_or_create_using_magento_id(
                cursor, user, int(other_magento_categ),
                context=context
            ) and category_obj.find_or_create_using_magento_id(
                cursor, user, int(other_magento_categ),
                context=context
            ).id or False
                    if categ_to_append:
                        other_categ_ids.append(categ_to_append)
        
        # Additional Functionality
        
        product_attribute_dict = {}
        
        with magento.ProductAttributeSet(instance.url, instance.api_user, instance.api_key) as attribute_set_api:
            default_attribute_set = filter(lambda attribute_set:  attribute_set['name']=='Default', attribute_set_api.list())[0]
            if not int(default_attribute_set['set_id']) == int(product_data['set']):
                product_attribute_dict = self.update_attributes(cursor, user, product, product_data, int(product_data['set']), context=context)
        if product_attribute_dict:
            product_values.update(product_attribute_dict)
            
        #Add the other category ids under many2many field for other category fields
        if other_categ_ids:
            if product.categ_id.id in other_categ_ids:
                other_categ_ids = other_categ_ids.remove(product.categ_id.id)
            product_values.update({'other_product_category_ids': [(6, 0, other_categ_ids)]})
                
            self.write(local_cr, user, product.id, product_values, context=context)
        
        #Rebrowse the record
        product = self.browse(local_cr, user, product.id, context=context)
        website_product_ids = prod_website_obj.search(local_cr, user, [('product', '=', product.id)], context=context)
        if website_product_ids:
            prod_website_obj.write(local_cr, user, website_product_ids, {'gt_product': datetime.now()}, context=context)
        local_cr.commit()
        local_cr.close()
        return product

Product()

class MagentoWebsiteProduct(osv.Model):
    """Magento Website - Product store

    This model keeps a record of a product's association with a website and
    the ID of product on that website
    """
    _inherit = 'magento.website.product'

    _columns = dict(
        gt_product=fields.datetime(
            'Last Updated On',
        ),
    )
MagentoWebsiteProduct()              
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: