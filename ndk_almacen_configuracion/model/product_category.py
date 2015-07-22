# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Humanytek (<http://humanytek.com>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
import re

class product_category_ndk(osv.Model):

    _inherit = 'product.category'
    _description = 'Add fields into product.category'
    _columns = {
        'mage_categ_id': fields.integer('Magento category ID'),
        'mage_parent_categ_id': fields.integer('Magento parent category ID'),
        'import_from_magento': fields.boolean('Import from Magento'),
        'mage_path': fields.char('Magento path', size=1024),
        'mage_url_key': fields.char('Magento URL key'),
        'mage_url_path': fields.char('Magento URL path'),
    }
    _defaults = {
        'import_from_magento': True
    }
    
product_category_ndk()
