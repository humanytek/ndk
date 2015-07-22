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

# OpenERP
from openerp.osv import fields, osv

# Python
import time
import openerp
import codecs
import mysql.connector
import base64, urllib
import logging
_logger = logging.getLogger(__name__)


class sale_order_ndk(osv.Model):

    _inherit = 'sale.order'
    _description = 'Fields added into sale_order table'
    _columns = {
        'mage_order_id': fields.integer('ID Order Magento'),
        'mage_order_ref': fields.char('Ref. Number Order Magento')
    }
    
sale_order_ndk()


class sale_order_line_ndk(osv.Model):

    _inherit = 'sale.order.line'
    _description = 'Fields added into sale_order_line table'
    _columns = {
        'mage_order_id': fields.integer('ID Order Magento')
    }
    
sale_order_line_ndk()
