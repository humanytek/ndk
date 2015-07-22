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
from osv import fields, osv
from datetime import datetime
import html2text as ht

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'enable_ep': fields.boolean('Add Electrical Properties'),
        'made_in': fields.char('Made in', size=128),
        'model': fields.char('Model', size=64),
        'brand': fields.char('Brand', size=64), 
        'content': fields.char('Content', size=64),
        'electrical_properties': fields.text('Electrical Characteristics'),
        'type_lighting': fields.selection([('1', 'LUMINARIO COLGANTE'), ('2', 'LUMINARIO DE MESA'), ('3', 'LUMINARIO DE PARED'), ('4', 'LUMINARIO DE PISO')], 'Type Lighting')
        
        }

    def _get_barcode_template(self):
        return """
         ^XA
^DFR:BARCODE.GRF^FS

^FO30,20^BY2^B3N,,100^FN1^FS(barcode)
^FO30,150^A0N,20,20^FN5^FS (description)

^XZ"""
    def _get_package_template(self):
        return """
         ^XA
^DFR:PACKAGE.GRF^FS
^FO30,20^A0N,16,16^FN1^FS
^FO30,40^A0N,16,16^FDRazon Social del Importador^FS
^FO30,60^A0N,16,16^FDScandinavian Design Center SA de CV^FS
^FO30,80^A0N,16,16^FN2^FS (street)
^FO120,80^A0N,16,16^FN3^FS (street2)
^FO160,80^A0N,16,16^FN4^FS (mxcity2)
^FO30,100^A0N,16,16^FN5^FS (city)
^FO130,100^A0N,16,16^FN6^FS (state)
^FO190,100^A0N,16,16^FN8^FS (zip)
^FO270,100^A0N,16,16^FN7^FS (country)
^FO30,120^A0N,16,16^FDHecho en:^FS
^FO110,120^A0N,16,16^FN9^FS (made_in)
^FO30,160^A0N,16,16^FDModelo:^FS
^FO85,160^A0N,16,16^FN10^FS (model)
^FO30,180^A0N,16,16^FDCantidad:^FS
^FO100,180^A0N,16,16^FN11^FS (content)
^FO30,140^A0N,16,16^FDMarca:^FS
^FO80,140^A0N,16,16^FN12^FS (brand)
^FO30,200^A0N,16,16^FDCaracteristicas Electricas:^FS
^FO230,200^A0N,16,16^FN14^FS (electrical_properties)
^XZ
"""
     
    def _get_product_template(self):
        return """
         ^XA
^DFR:PACKAGE.GRF^FS
^FO30,30^A0N,20,20^FDNombre del Importador^FS
^FO30,50^A0N,20,20^FDScandinavian Design Center SA de CV^FS
^FO30,70^A0N,20,20^FN2^FS (street)
^FO125,70^A0N,20,20^FN3^FS (street2)
^FO170,70^A0N,20,20^FN4^FS (mxcity2)
^FO30,90^A0N,20,20^FN5^FS (city)
^FO130,90^A0N,20,20^FN6^FS (state)
^FO190,90^A0N,20,20^FN8^FS (zip)
^FO280,90^A0N,20,20^FN7^FS (country)
^FO30,130^A0N,20,20^FDModelo:^FS
^FO110,130^A0N,20,20^FN10^FS (model)
^FO30,110^A0N,20,20^FDMarca:^FS
^FO85,110^A0N,20,20^FN11^FS (brand)
^FO30,150^A0N,20,20^FDCaracteristicas Electricas:^FS
^FO240,150^A0N,20,20^FN14^FS (electrical_properties)
^XZ
"""
    
    def _get_barcode_value(self, cr, uid, ids, context=None):
        template = """
^XA
^XFR:BARCODE.GRF
^FN1^FD%(ean13)s^FS
^FN2^FD%(default_code)s^FS
^FN5^FD%(description)s^FS
^XZ"""
        return template
    def _get_product_value(self, cr, uid, ids, context=None):
        template = """
^XA
^XFR:PACKAGE.GRF
^FN1^FD%(name)s^FS
^FN2^FD%(street)s^FS
^FN3^FD%(street2)s^FS
^FN4^FD%(mxcity2)s^FS
^FN5^FD%(city)s,^FS
^FN6^FD%(state)s^FS
^FN7^FD%(country)s^FS
^FN8^FD%(zip)s^FS
^FN9^FD%(made_in)s^FS
^FN10^FD%(model)s^FS
^FN11^FD%(content)s^FS
^FN12^FD%(brand)s^FS
^FN13^FD%(code)s^FS
^FN14^AD^FH/^FD%(electrical_properties)s^FS

^XZ"""
        return template

    def _get_product_label_value(self, cr, uid, ids, context=None):
        template = """
^XA
^XFR:PACKAGE.GRF
^FN1^FD%(name)s^FS
^FN2^FD%(street)s^FS
^FN3^FD%(street2)s^FS
^FN4^FD%(mxcity2)s^FS
^FN5^FD%(city)s,^FS
^FN6^FD%(state)s^FS
^FN7^FD%(country)s^FS
^FN8^FD%(zip)s^FS
^FN9^FD%(made_in)s^FS
^FN10^FD%(model)s^FS
^FN11^FD%(brand)s^FS
^FN12^FD%(code)s^FS
^FN14^AD^FH/^FD%(electrical_properties)s^FS
^XZ"""
        return template
    
    
    def get_zpl_command(self, cr, uid, ids, context=None):
        zpl_result = {
            'package': self._get_package_template(),
            'result': [],  
            }
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = []
        for product in self.browse(cr, uid, ids, context=context):
            luminaro_dict = {
                    '1': 'LUMINARIO COLGANTE',
                    '2': 'LUMINARIO DE MESA',
                    '3': 'LUMINARIO DE PARED',
                    '4': 'LUMINARIO DE PISO'         
                    }
            if product.type_lighting:
                
                type_lighting_name = luminaro_dict[product.type_lighting]
            else:
                type_lighting_name = ''
                
            code = product.default_code
            electrical_properties = product.electrical_properties
            if product.electrical_properties:
                if product.electrical_properties.find('~') <> -1:
                    electrical_properties = product.electrical_properties.replace('~' , '/7E')
            zpl_vals = {
                'name': type_lighting_name,
                'code': product.default_code and product.default_code or '',
                'business_importer': product.company_id.partner_id and product.company_id.partner_id.name or '',
                'currency': product.company_id.currency_id and product.company_id.currency_id.name or '',
                'street': product.company_id.street or '',
                'street2': product.company_id.street2 or '',
                'mxcity2': product.company_id.l10n_mx_city2 or '',
                'city': product.company_id.city or '',
                'state': product.company_id.state_id and product.company_id.state_id.name or '',
                'zip': product.company_id.zip or '',
                'country': product.company_id.country_id and product.company_id.country_id.name or '',
                'default_code': product.default_code or '',
                'made_in': product.made_in or '', 
                'model': product.model or '',
                'content': product.content or '',
                'brand': product.brand or '',
                'electrical_properties': electrical_properties or '',
            }
            template = self._get_product_value(cr, uid, ids, context=context)
            temp = template%zpl_vals
            result.append(('package', temp))
            printed_date = "Printed On " + datetime.now().strftime("%d/%m/%Y")
#             self.write(cr, uid, [product.id], {'printed_on': printed_date}, context=context)
#             file_name = self._create_temp_file(temp, product.reg_no) 
#             result.append((registrant.type, file_name));
        zpl_result['result'] = result
        return zpl_result
    
    def get_zpl_product_command(self, cr, uid, ids, context=None):
        zpl_result = {
            'product_label': self._get_product_template(),
            'result': [],  
            }
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = []
        for product in self.browse(cr, uid, ids, context=context):
            first_name = product.name
            code = product.default_code
            electrical_properties = product.electrical_properties
            if product.electrical_properties.find('~') <> -1:
                electrical_properties = product.electrical_properties.replace('~' , '/7E')
            zpl_vals = {
                'name': first_name,
                'code': product.default_code and product.default_code or '',
                'business_importer': product.company_id.partner_id and product.company_id.partner_id.name or '',
                'currency': product.company_id.currency_id and product.company_id.currency_id.name or '',
                'street': product.company_id.street or '',
                'street2': product.company_id.street2 or '',
                'mxcity2': product.company_id.l10n_mx_city2 or '',
                'city': product.company_id.city or '',
                'zip': product.company_id.zip or '',
                'state': product.company_id.state_id and product.company_id.state_id.name or '',
                'country': product.company_id.country_id and product.company_id.country_id.name or '',
                'default_code': product.default_code or '',
                'made_in': product.made_in or '', 
                'model': product.model or '',
                'content': product.content or '',
                'brand': product.brand or '',
                'electrical_properties': electrical_properties or '',
            }
            template = self._get_product_label_value(cr, uid, ids, context=context)
            temp = template%zpl_vals
            result.append(('product_label', temp))
            printed_date = "Printed On " + datetime.now().strftime("%d/%m/%Y")
#             self.write(cr, uid, [product.id], {'printed_on': printed_date}, context=context)
#             file_name = self._create_temp_file(temp, product.reg_no) 
#             result.append((registrant.type, file_name));
        zpl_result['result'] = result
        return zpl_result
    
    def get_zpl_barcode(self, cr, uid, ids, context=None):
        zpl_result = {
            'barcode': self._get_barcode_template(),
            'result': [],  
            }
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = []
        for product in self.browse(cr, uid, ids, context=context):
            code = product.default_code
            zpl_vals = {
                'ean13': product.default_code or '',
                'default_code': product.default_code or '',
                'description':product.short_description and ht.html2text(product.short_description) or'',
                
            }
            template = self._get_barcode_value(cr, uid, ids, context=context)
            temp = template%zpl_vals
            result.append(('barcode', temp))
            printed_date = "Printed On " + datetime.now().strftime("%d/%m/%Y")
        zpl_result['result'] = result
        return zpl_result
    
    def _create_temp_file(self, zpl_string, reg_no):
        file_name = os.path.join('jzebra/static/lib', 'zpl_' + (reg_no or '') + '.txt')
        file = os.path.join(ADDONS_PATH, file_name)
        with codecs.open(file, 'w+', encoding='cp1252') as f:
            f.write(zpl_string)
        return file_name
    
    def _get_corrected_name(self, name):
        if not name:
            return ''
        name = unidecode(name)
        name = name.upper()
        return name
product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: