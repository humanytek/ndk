# -*- encoding: utf-8 -*-# -*- encoding: utf-8 -*-
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
from openerp.osv import osv
from openerp.tools.translate import _

import threading
import logging
import magento
import math
import datetime

class UpdateCatalog(osv.TransientModel):
    
    _inherit = 'magento.instance.update_catalog'
    
    def update_products(self, cursor, user, website_id, imported_magento_ids, context#, use_local_cr=False
                        ):
        """
        Updates products for current website

        :param cursor: Database cursor
        :param user: ID of current user
        :param website: Browse record of website
        :param context: Application context
        :return: List of product IDs
        """
        local_cr = cursor
#         if use_local_cr:
#             db = openerp.sql_db.db_connect(cursor.dbname)
#             local_cr = db.cursor()
            
        website_obj = self.pool.get('magento.instance.website')
        product_obj = self.pool.get('product.product')
        prod_website_obj = self.pool.get('magento.website.product')
        
        website = website_obj.browse(local_cr, user, website_id, context)
        context.update({
            'magento_website': website.id
        })

        products = []
        
        _logger = logging.getLogger('Update Products Magento -> OpenERP')
        
        instance = website.instance
        magento_api = magento.Product(instance.url, instance.api_user, instance.api_key)
        
        magento_products = website.magento_products
        if website.last_updated_magento_to_openerp: #Filter on the basis of last updated details on magento
            magento_link_ids_in_openerp = [x.magento_id for x in website.magento_products]
            with magento_api as product_api:
                filtered_products = product_api.list(filters={'updated_at':{'gt': website.last_updated_magento_to_openerp}}, store_view=None)
                filtered_magento_ids = [int(x['product_id']) for x in filtered_products]
            magento_ids_to_update = list(set(magento_link_ids_in_openerp) & set(filtered_magento_ids))
            #magento_ids_to_update = filter(lambda x: x not in imported_magento_ids, magento_ids_to_update)
            magento_product_ids_total = prod_website_obj.search(local_cr, user, [('magento_id','in',magento_ids_to_update)], context=context)
            magento_product_ids = prod_website_obj.search(local_cr, user, [('magento_id','in',magento_ids_to_update)], limit=500, offset=4019, context=context)
            magento_products = prod_website_obj.browse(local_cr, user, magento_product_ids, context=context)
        #Removing just imported magento products from updation list
        magento_products = [x for x in magento_products if x.magento_id not in imported_magento_ids]
        
        # splitting the magento_products array in subarrays to avoid memory leaks in case of massive upload
        l = 200
        f = lambda v, l: [v[i * l:(i + 1) * l] for i in range(int(math.ceil(len(v) / float(l))))]
        split_magento_products = f(magento_products, l)
        
        total_mag_products = len(magento_products)
        
        count = 1
        for magento_products in split_magento_products:
            for mag_product in magento_products:
                _logger.info('Updating %s - %s/%s' % (mag_product.product.name,count,total_mag_products))
                products.append(
                    product_obj.update_from_magento(
                        local_cr, user, mag_product.product, magento_api, website, context=context
                    )
                )
                count += 1
        
        website_obj.write(local_cr, user, [website_id], {
                                                  'last_updated_magento_to_openerp': datetime.datetime.now(),
                                                  })

#         if use_local_cr:
#             local_cr.commit()
#             local_cr.close()
        
        return map(int, products)
UpdateCatalog()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: