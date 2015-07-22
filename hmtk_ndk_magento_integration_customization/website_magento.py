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

class InstanceWebsite(osv.Model):
    _inherit = 'magento.instance.website'
    
    def import_and_update_products(self, cursor, user, ids=None, context=None):
        """
        Import and update the products from magento.
        
        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of website ids
        :param context: Dictionary of application context
        """
        if context is None:
            context = {}
        import_and_update_catalog_obj = self.pool.get('magento.instance.import_catalog')
        if not ids:
            ids = self.search(cursor, user, [], context)
        
        for website in self.browse(cursor, user, ids, context):
            import_and_update_catalog_id = import_and_update_catalog_obj.create(cursor, user, {'import_images': True}, context)
            context['active_id'] = website.id
            import_and_update_catalog_obj.import_and_update_products(cursor, user, [import_and_update_catalog_id], context)
            
    
    def export_and_update_products(self, cursor, user, ids=None, context=None):
        """
        Export and update the products to magento.
        
        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of website ids
        :param context: Dictionary of application context
        """
        if context is None:
            context = {}
        export_and_update_catalog_obj = self.pool.get('magento.instance.website.export_catalog')
        if not ids:
            ids = self.search(cursor, user, [], context)
        
        for website in self.browse(cursor, user, ids, context):
            context['active_id'] = website.id
            attribute_set = export_and_update_catalog_obj._get_default_attribute_set(cursor, user, context=context)
            export_and_update_catalog_id = export_and_update_catalog_obj.create(cursor, user, {'export_images': True, 'attribute_set': attribute_set}, context)
            export_and_update_catalog_obj.update_and_export_products_openerp_to_magento(cursor, user, [export_and_update_catalog_id], context)

InstanceWebsite()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: