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

import xmlrpclib
from copy import deepcopy
import time

import openerp
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import magento
#from .api import OrderConfig

import logging
_logger = logging.getLogger(__name__)

import mysql.connector


class magento_instance_ndk(osv.Model):

    _inherit = 'magento.instance'
    _description = 'Add fields Magento configuration'
    _columns = {
        'mage_user': fields.char('User root Magento'),
        'mage_pass': fields.char('Password user root Magento'),
        'mage_host': fields.char('URL connection to Magento'),
        'mage_db': fields.char('DB Magento to connect'),
    }
        
magento_instance_ndk()
    
