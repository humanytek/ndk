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


class res_partner_ndk(osv.Model):

    _inherit = 'res.partner'
    _description = 'Fields added into res_partner table'
    _columns = {
        'mage_id_customer': fields.integer('ID Customer Magento')
    }
    _sql_constraints = [
        ('mage_id_customer_uniq', 'unique(mage_id_customer)', 'Este campo debe ser unico')
    ]
    
    # 15/07/2015 (felix) Metodo para actualizar datos del cliente Magento->OpenERP
    def update_customer_magento_openerp(self, cr, uid, ids, context=None):
    
        # ID del cliente
        self_id_customer = self.browse(cr, uid, ids[0], context)['id']
        mage_id_customer = self.browse(cr, uid, ids[0], context)['mage_id_customer']
        
        # Datos de conexion
        obj_magento_instance = self.pool.get('magento.instance')
        src_magento_instance = obj_magento_instance.search(cr, uid, [('active', '=', True)], limit=1)
        if src_magento_instance:
            mage_user = obj_magento_instance.browse(cr, uid, src_magento_instance[0], context)['mage_user']
            mage_pass = obj_magento_instance.browse(cr, uid, src_magento_instance[0], context)['mage_pass']
            mage_host = obj_magento_instance.browse(cr, uid, src_magento_instance[0], context)['mage_host']
            mage_db = obj_magento_instance.browse(cr, uid, src_magento_instance[0], context)['mage_db']
            mage_url = obj_magento_instance.browse(cr, uid, src_magento_instance[0], context)['url']
        else:
            raise osv.except_osv('Advertencia','Debe crear una instancia para la conexion')
            return {}
        
        cnx = mysql.connector.connect(user=str(mage_user),password='qBg#@kme@#$r',host=str(mage_host),database=str(mage_db))
        if not cnx:
            raise osv.except_osv('Advertencia','No se produjo conexion')
            return {}
        cursor = cnx.cursor()
        if cursor:        
            crm_result = []
            q_customers = ('SELECT entity_id,email FROM mage_customer_entity WHERE entity_id='+str(mage_id_customer))
            cursor.execute(q_customers)
            customers = cursor.fetchall()
            for crm in customers:
                if crm[0] <> None:
                    
                    crm_id = crm[0]
                    crm_email = crm[1]
                    
                    # Nombre completo del cliente
                    q_full_name = ("SELECT t2.value \n"
                        "FROM mage_customer_entity_varchar AS t2 \n"
                        "INNER JOIN mage_eav_attribute AS t3 \n"
                        "WHERE t2.entity_id = "+str(crm_id)+" \n"
                        "AND t2.attribute_id = t3.attribute_id \n"
                        "AND (t3.attribute_code LIKE 'firstname' OR t3.attribute_code LIKE 'lastname')")                        
                    cursor.execute(q_full_name)
                    full_name = cursor.fetchall()
                    crm_full_name = ''
                    for fn in full_name:
                        if fn <> None:
                            crm_full_name += fn[0]+' '
                    
                    # Company, Ciudad, Pais, Estado, Codigo postal, Telefono, Fax, RFC
                    q_datos = ("SELECT t1.entity_id,t1.value,t2.attribute_code \n"
                        "FROM mage_customer_address_entity_varchar AS t1  \n"
                        "INNER JOIN mage_eav_attribute AS t2 \n"
                        "WHERE t1.entity_id="+str(crm_id)+" \n"
                        "AND t1.attribute_id=t2.attribute_id \n"
                        "AND (t2.attribute_code LIKE 'company' \n"
                        "OR t2.attribute_code LIKE 'city' \n"
                        "OR t2.attribute_code LIKE 'country_id' \n"
                        "OR t2.attribute_code LIKE 'region' \n"
                        "OR t2.attribute_code LIKE 'postcode' \n"
                        "OR t2.attribute_code LIKE 'telephone' \n"
                        "OR t2.attribute_code LIKE 'fax' \n"
                        "OR t2.attribute_code LIKE 'rfc')")
                    cursor.execute(q_datos)
                    datos_dir = cursor.fetchall()
                    crm_company = ''
                    crm_city = ''
                    crm_country = ''
                    crm_state = ''
                    crm_zip = ''
                    crm_phone = ''
                    crm_fax = ''
                    crm_vat = ''
                    for dt in datos_dir:
                        if dt[0] <> None:
                            if dt[2] == 'company':
                                crm_company_id = dt[1]
                            if dt[2] == 'city':
                                crm_city = dt[1]
                            if dt[2] == 'country_id':
                                crm_country = dt[1]
                            if dt[2] == 'region':
                                crm_state = dt[1]
                            if dt[2] == 'postcode':
                                crm_zip = dt[1]
                            if dt[2] == 'telephone':
                                crm_phone = dt[1]
                            if dt[2] == 'fax':
                                crm_fax = dt[1]
                            if dt[2] == 'rfc':
                                crm_vat = dt[1]
                                
                    # Obtener ID de pais en OpenERP
                    obj_res_country = self.pool.get('res.country')
                    src_res_country = obj_res_country.search(cr, uid, ['|',('name','=',crm_country),('code','=',crm_country)], limit=1)
                    if src_res_country:
                        crm_country_id = obj_res_country.browse(cr, uid, src_res_country[0], context)['id']
                    else:
                        crm_country_id = ''
                    
                    # Obtener ID de estado en OpenERP
                    obj_res_country_state = self.pool.get('res.country.state')
                    src_res_country_state = obj_res_country_state.search(cr, uid, ['|',('name','=',crm_state),('code','=',crm_state)], limit=1)
                    if src_res_country_state:
                        crm_state_id = obj_res_country.browse(cr, uid, src_res_country_state[0], context)['id']
                    else:
                        crm_state_id = ''
                                
                    # Captura de la calle
                    q_street = ("SELECT value FROM mage_customer_address_entity_text WHERE entity_id="+str(crm_id))
                    cursor.execute(q_street)
                    street = cursor.fetchall()
                    crm_street = ''
                    for stt in street:
                        if stt[0] <> None:
                            crm_street = stt[0]
                    
                    crm_values = {
                        'name': crm_full_name.title(),
                        'email': crm_email,
                        'street': crm_street.title(),
                        'city': crm_city.title(),
                        'country_id': crm_country_id,
                        'state_id': crm_state_id,
                        'zip': crm_zip,
                        'phone': crm_phone,
                        'fax': crm_fax,
                        #'vat': crm_vat,
                        'mage_id_customer': crm_id
                    }
                    '''
                    crm_full_name = ''
                    crm_email = ''
                    crm_street = ''
                    crm_city = ''
                    crm_country_id = ''
                    crm_state_id = ''
                    crm_zip = ''
                    crm_phone = ''
                    crm_fax = ''
                    crm_vat = ''
                    crm_id = ''
                    '''                             
            # Cargar datos de clientes en base OpenERP
            self.write(cr, uid, [self_id_customer], crm_values, context)
        
        return True

    
res_partner_ndk()
