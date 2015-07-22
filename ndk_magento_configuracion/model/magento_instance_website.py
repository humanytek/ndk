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

# Python
import xmlrpclib
from copy import deepcopy
import time
import openerp
import codecs
import mysql.connector
import base64, urllib
import logging
_logger = logging.getLogger(__name__)

# OpenERP
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import magento

class magento_instance_website_ndk(osv.Model):

    _inherit = 'magento.instance.website'
    _description = 'Configuraciones conector Magento->OpenERP para Nordika'
    
    # 29/95/2015 (felix) Metodo para transferir informacion campo "metodo" de Magento a OpenERP
    #def trans_magento_openerp(self, cr, uid, ids, context=None):
    def trans_categ_magento_openerp(self, cr, uid, ids, context=None):
    
        # Datos de instancia web
        id_root_category = self.browse(cr, uid, ids[0], context)['magento_root_category_id']
    
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
    
        #cnx = mysql.connector.connect(user='root', password='qBg#@kme@#$r', host='127.0.0.1', database='nordamx_store')
        cnx = mysql.connector.connect(user=str(mage_user),password='qBg#@kme@#$r',host=str(mage_host),database=str(mage_db))
        if not cnx:
            raise osv.except_osv('Advertencia','No se produjo conexion')
            return {}
        cursor = cnx.cursor()
        if cursor:
                
            # Disposicion de tablas en OpenERP
            obj_product_product = self.pool.get('product.product')
            obj_product_template = self.pool.get('product.template')
            obj_product_category = self.pool.get('product.category')
            obj_res_partner = self.pool.get('res.partner')
                        
            #####################################################################
            # Construccion query para actualizar categorias
            #####################################################################
            q_categories = ("SELECT name,entity_id,is_active,parent_id,path,url_key,url_path FROM mage_catalog_category_flat_store_1 ORDER BY entity_id")
            cursor.execute(q_categories)
            categorias = cursor.fetchall()
            for categ in categorias:
                if categ[0] <> 'None':
                    #src_product_category = obj_product_category.search(cr, uid, [('name', 'like', categ[0])])
                    src_product_category = obj_product_category.search(cr, uid, [('mage_categ_id', '=', categ[1])])
                    
                    # Categoria padre y relacion en OpenERP
                    src_product_categ_parent = obj_product_category.search(cr, uid, [('mage_categ_id', '=', categ[3])])
                    if src_product_categ_parent:
                        id_product_categ_parent = obj_product_category.browse(cr, uid, src_product_categ_parent[0], context)['id']
                    else:
                        id_product_categ_parent = 0
                        
                    if src_product_category:
                        id_product_category = obj_product_category.browse(cr, uid, src_product_category[0], context)['id']
                        values = {
                            'name': categ[0],
                            'mage_categ_id': categ[1],
                            'active': categ[2],
                            'mage_parent_categ_id': categ[3],
                            'mage_path': categ[4],
                            'mage_url_key': categ[5],
                            'mage_url_path': categ[6],
                            'parent_id': id_product_categ_parent,
                        }
                        obj_product_category.write(cr, uid, [id_product_category], values, context)
                    else:                            
                        values = {
                            'name': categ[0],
                            'mage_categ_id': categ[1],
                            'active': categ[2],
                            'mage_parent_categ_id': categ[3],
                            'mage_path': categ[4],
                            'mage_url_key': categ[5],
                            'mage_url_path': categ[6],
                            'parent_id': id_product_categ_parent,
                        }
                        obj_product_category.create(cr, uid, values, context)
                        
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return True
                  
    # 13/07/2015 (felix) Metodo para transferir informacion de productos de Magento a OpenERP
    def trans_prod_magento_openerp(self, cr, uid, ids, context=None):
        # Datos de instancia web
        id_root_category = self.browse(cr, uid, ids[0], context)['magento_root_category_id']
    
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
    
        #cnx = mysql.connector.connect(user='root', password='qBg#@kme@#$r', host='127.0.0.1', database='nordamx_store')
        cnx = mysql.connector.connect(user=str(mage_user),password='qBg#@kme@#$r',host=str(mage_host),database=str(mage_db))
        if not cnx:
            raise osv.except_osv('Advertencia','No se produjo conexion')
            return {}
        cursor = cnx.cursor()
        if cursor:
                
            # Disposicion de tablas en OpenERP
            obj_product_product = self.pool.get('product.product')
            obj_product_template = self.pool.get('product.template')
            obj_product_category = self.pool.get('product.category')
            obj_res_partner = self.pool.get('res.partner')
            
            #####################################################################
            # Tomar y cargar productos y sus respectivos atributos
            #####################################################################
            q_prod = ("SELECT t1.entity_id,t1.name,t1.sku,t1.short_description,t1.type_id,t1.price,t1.url_key,t1.url_path, \n"
                "t1.color_value,t1.disenador_value,t1.manufacturer_value,t1.color_2_value,t1.cojin_value,t1.colorcojin_value,t1.color_tela_value, \n"
                "t1.thumbnail \n"
                "FROM mage_catalog_product_flat_1 AS t1 \n"
                "ORDER BY entity_id ASC")
            cursor.execute(q_prod)
            productos = cursor.fetchall()
            prod_result = []
            prod_modelo_tec = ''
            prod_description_sale = ''
            prod_images_all = []
            for p in productos:
                if p[0] <> None:
                
                    # Valores propios del producto de Magento
                    prod_id = p[0]
                    prod_name = p[1]
                    prod_sku = p[2]
                    prod_short_description = p[3]
                    prod_type = p[4]
                    prod_price = p[5]
                    prod_url_key = p[6]
                    prod_url_path = p[7]
                    
                    # Obtener y concatenar valores de atributos del producto de Magento
                    if p[8] <> None and p[8] <> 'NULL' and p[8] <> 'no_selection' and p[8] <> '/':
                        prod_description_sale += codecs.encode(p[8],'utf8')+'; '
                    if p[9] <> None and p[9] <> 'NULL' and p[9] <> 'no_selection' and p[9] <> '/':
                        prod_description_sale += codecs.encode(p[9],'utf8')+'; '
                    if p[10] <> None and p[10] <> 'NULL' and p[10] <> 'no_selection' and p[10] <> '/':
                        prod_description_sale += codecs.encode(p[10],'utf8')+'; '
                    if p[11] <> None and p[11] <> 'NULL' and p[11] <> 'no_selection' and p[11] <> '/':
                        prod_description_sale += codecs.encode(p[11],'utf8')+'; '
                    if p[12] <> None and p[12] <> 'NULL' and p[12] <> 'no_selection' and p[12] <> '/':
                        prod_description_sale += codecs.encode(p[12],'utf8')+'; '
                    if p[13] <> None and p[13] <> 'NULL' and p[13] <> 'no_selection' and p[13] <> '/':
                        prod_description_sale += codecs.encode(p[13],'utf8')+'; '
                    if p[14] <> None and p[14] <> 'NULL' and p[14] <> 'no_selection' and p[14] <> '/':
                        prod_description_sale += codecs.encode(p[14],'utf8')+'; '
                    
                    # Obtener valores de atributos alternativos de Magento
                    q_attrs = ("SELECT t2.value,t1.value \n"
                        "FROM mage_catalog_product_entity_varchar AS t1 \n"
                        "INNER JOIN mage_eav_attribute_label AS t2 \n"
                        "ON t1.attribute_id = t2.attribute_id \n"
                        "AND t1.entity_id = "+str(prod_id)+" \n"
                        "AND t1.value <> 'NULL' \n"
                        "AND t1.value <> '/' \n"
                        "AND t1.value <> 'no_selection' \n"
                        "ORDER BY entity_id ASC")
                    cursor.execute(q_attrs)
                    attrs = cursor.fetchall()
                    for a in attrs:
                        if a[0] <> None:
                            if a[0] == 'Modelo' and a[1] <> None:
                                prod_modelo_tec = a[1]
                            elif a[1] <> None:
                                prod_description_sale += codecs.encode(a[1],'utf8')+'; '
                                
                    # Obtener ID de categoria del Producto en Magento
                    prod_mage_categ_id = id_root_category
                    q_categ = ("SELECT category_id FROM mage_catalog_category_product WHERE product_id="+str(prod_id))
                    cursor.execute(q_categ)
                    categories = cursor.fetchall()
                    for c in categories:
                        if c[0] <> None:
                            prod_mage_categ_id = c[0]
                            
                    # Relacion categoria Magento en OpenERP
                    src_product_category = obj_product_category.search(cr, uid, [('mage_categ_id', '=', prod_mage_categ_id)])
                    if src_product_category:
                        id_product_category = obj_product_category.browse(cr, uid, src_product_category[0], context)['id']
                    else:
                        src_product_category = obj_product_category.search(cr, uid, [('mage_categ_id', '=', id_root_category)])
                        id_product_category = obj_product_category.browse(cr, uid, src_product_category[0], context)['id']
                        
                    # Obtener el estatus del producto en Magento
                    q_status = ("SELECT t2.value FROM mage_eav_attribute AS t1 \n"
                        "INNER JOIN mage_catalog_product_entity_int AS t2 \n"
                        "WHERE t2.entity_id = "+str(prod_id)+" \n"
                        "AND t1.attribute_code = 'status' \n"
                        "AND t1.attribute_id = t2.attribute_id")
                    cursor.execute(q_status)
                    status = cursor.fetchall()
                    for s in status:
                        if s[0] == 1:
                            prod_active_in_magento = True
                        else:
                            prod_active_in_magento = False                            
                        
                    # Manipulacion de imagenes
                    prod_image_url = urllib.urlopen(mage_url+'media/catalog/product'+str(p[15]))
                    if prod_image_url:
                        prod_image = base64.encodestring(prod_image_url.read())
                        prod_image_url.close()
                        q_image_update = "UPDATE product_product SET image='"+prod_image+"',image_small='"+prod_image+"',image_medium='"+prod_image+"' WHERE mage_product_id="+str(prod_id)
                        cr.execute(q_image_update)
                    
                    # Valores para llenar en OpenERP
                    valores = {
                        'mage_product_id': prod_id,
                        'name': prod_name,
                        'name_template': prod_name,
                        'default_code': prod_sku,
                        'description': prod_short_description,
                        'short_description': prod_short_description,
                        'magento_product_type': prod_type,
                        'list_price': prod_price,
                        'mage_url_key': prod_url_key,
                        'mage_url_path': prod_url_path,
                        'modelo_tec': prod_modelo_tec,
                        'description_sale': prod_description_sale,
                        'mage_categ_id': prod_mage_categ_id,
                        'categ_id': id_product_category,
                        'active_in_magento': prod_active_in_magento
                    }
                    prod_result.append(valores)
                    
                    # Limpiar variables temporales
                    prod_id = ''
                    prod_name = ''
                    prod_sku = ''
                    prod_short_description = ''
                    prod_type = ''
                    prod_price = ''
                    prod_url_key = ''
                    prod_url_path = ''
                    prod_description_sale = ''
                    prod_modelo_tec = ''
                    prod_mage_categ_id = ''
                    prod_image = ''
                    prod_active_in_magento = ''
                    
            # Cargar datos en base OpenERP
            for p in prod_result:
                #src_product_product = obj_product_product.search(cr, uid, [('default_code', '=', p['default_code'])])
                src_product_product = obj_product_product.search(cr, uid, [('mage_product_id','=',p['mage_product_id']),('active','=',True)])
                if src_product_product:
                    id_product_product = obj_product_product.browse(cr, uid, src_product_product[0], context)['id']
                    obj_product_product.write(cr, uid, [id_product_product], p, context)
                elif p['mage_product_id'] <> None:
                    obj_product_product.create(cr, uid, p, context)
                
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return True
        
    # 14/07/2015 (felix) Metodo para transferir informacion de clientes de Magento a OpenERP
    def trans_customers_magento_openerp(self, cr, uid, ids, context=None):
        # Datos de instancia web
        id_root_category = self.browse(cr, uid, ids[0], context)['magento_root_category_id']
    
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
    
        #cnx = mysql.connector.connect(user='root', password='qBg#@kme@#$r', host='127.0.0.1', database='nordamx_store')
        cnx = mysql.connector.connect(user=str(mage_user),password='qBg#@kme@#$r',host=str(mage_host),database=str(mage_db))
        if not cnx:
            raise osv.except_osv('Advertencia','No se produjo conexion')
            return {}
        cursor = cnx.cursor()
        if cursor:
                
            # Disposicion de tablas en OpenERP
            obj_product_product = self.pool.get('product.product')
            obj_product_template = self.pool.get('product.template')
            obj_product_category = self.pool.get('product.category')
            obj_res_partner = self.pool.get('res.partner')
                        
            #####################################################################
            # Tomar y cargar clientes y sus respectivos atributos
            #####################################################################
            crm_result = []
            q_customers = ('SELECT entity_id,email FROM mage_customer_entity ORDER BY entity_id ASC')
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
                    crm_result.append(crm_values)
                    
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
                                                            
            # Cargar datos de clientes en base OpenERP
            for crm_item in crm_result:
                src_res_partner = obj_res_partner.search(cr, uid, [('mage_id_customer','=',crm_item['mage_id_customer'])])
                if src_res_partner:
                    id_res_partner = obj_res_partner.browse(cr, uid, src_res_partner[0], context)['id']
                    obj_res_partner.write(cr, uid, [id_res_partner], crm_item, context)
                elif crm_item['name'] <> None:
                    obj_res_partner.create(cr, uid, crm_item, context)
        
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return True

    
    # 16/07/2015 (felix) Metodo para crear un cliente si no existe
    def _create_new_customer(self, cr, uid, mage_id_customer, context):
        res = 0
        obj_res_partner = self.pool.get('res.partner')
        
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
            crm_values = {}
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
                            
                    # Obtener IDs de "Cuenta a cobrar" y "Cuenta a pagar"
                    # - Cuenta a cobrar: 1031-01-000 Clientes CXC
                    obj_account_account = self.pool.get('account.account')
                    src_cta_cobrar = obj_account_account.search(cr, uid, [('code','=','1031-01-000')])
                    id_cta_cobrar = obj_account_account.browse(cr, uid, src_cta_cobrar[0], context)['id']
                    # - Cuenta a pagar: 2010-01-001 Proveedores Extranjeros
                    src_cta_pagar = obj_account_account.search(cr, uid, [('code','=','2010-01-001')])
                    id_cta_pagar = obj_account_account.browse(cr, uid, src_cta_pagar[0], context)['id']                    
                    
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
                        'property_account_receivable': id_cta_cobrar,
                        'property_account_payable': id_cta_pagar,
                        'mage_id_customer': crm_id
                    }
                                        
                    # Cargar datos de clientes en base OpenERP
                    res = obj_res_partner.create(cr, uid, crm_values, context)
                    
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()        
        return res
        
    # 17/07/2015 (felix) Metodo para crear producto en OpenERP
    def _create_new_product(self, cr, uid, mage_product_id, context=None):
        res = 0
        # Disposicion de tablas en OpenERP
        obj_product_template = self.pool.get('product.template')
        obj_product_category = self.pool.get('product.category')
        obj_product_images = self.pool.get('product.images')
        obj_magento_instance_website = self.pool.get('magento.instance.website')
        
        # Datos de instancia web
        all_magento_instance_website = obj_magento_instance_website.search(cr, uid, [(1,'=',1)], limit=1)
        id_root_category = obj_magento_instance_website.browse(cr, uid, all_magento_instance_website[0], context)['magento_root_category_id']
        
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
            # Tomar y cargar productos y sus respectivos atributos
            q_prod = ("SELECT t1.entity_id,t1.name,t1.sku,t1.short_description,t1.type_id,t1.price,t1.url_key,t1.url_path, \n"
                "t1.color_value,t1.disenador_value,t1.manufacturer_value,t1.color_2_value,t1.cojin_value,t1.colorcojin_value,t1.color_tela_value, \n"
                "t1.thumbnail \n"
                "FROM mage_catalog_product_flat_1 AS t1 \n"
                "WHERE t1.entity_id="+str(mage_product_id))
            cursor.execute(q_prod)
            productos = cursor.fetchall()
            prod_result = []
            prod_modelo_tec = ''
            prod_description_sale = ''
            prod_images_all = []
            for p in productos:
                if p[0] <> None:
                    # Valores propios del producto de Magento
                    prod_id = mage_product_id
                    prod_name = p[1]
                    prod_sku = p[2]
                    prod_short_description = p[3]
                    prod_type = p[4]
                    prod_price = p[5]
                    prod_url_key = p[6]
                    prod_url_path = p[7]
                    
                    # Obtener y concatenar valores de atributos del producto de Magento
                    if p[8] <> None and p[8] <> 'NULL' and p[8] <> 'no_selection' and p[8] <> '/':
                        prod_description_sale += codecs.encode(p[8],'utf8')+'; '
                    if p[9] <> None and p[9] <> 'NULL' and p[9] <> 'no_selection' and p[9] <> '/':
                        prod_description_sale += codecs.encode(p[9],'utf8')+'; '
                    if p[10] <> None and p[10] <> 'NULL' and p[10] <> 'no_selection' and p[10] <> '/':
                        prod_description_sale += codecs.encode(p[10],'utf8')+'; '
                    if p[11] <> None and p[11] <> 'NULL' and p[11] <> 'no_selection' and p[11] <> '/':
                        prod_description_sale += codecs.encode(p[11],'utf8')+'; '
                    if p[12] <> None and p[12] <> 'NULL' and p[12] <> 'no_selection' and p[12] <> '/':
                        prod_description_sale += codecs.encode(p[12],'utf8')+'; '
                    if p[13] <> None and p[13] <> 'NULL' and p[13] <> 'no_selection' and p[13] <> '/':
                        prod_description_sale += codecs.encode(p[13],'utf8')+'; '
                    if p[14] <> None and p[14] <> 'NULL' and p[14] <> 'no_selection' and p[14] <> '/':
                        prod_description_sale += codecs.encode(p[14],'utf8')+'; '
                    
                    # Obtener valores de atributos alternativos de Magento
                    q_attrs = ("SELECT t2.value,t1.value \n"
                        "FROM mage_catalog_product_entity_varchar AS t1 \n"
                        "INNER JOIN mage_eav_attribute_label AS t2 \n"
                        "ON t1.attribute_id = t2.attribute_id \n"
                        "AND t1.entity_id = "+str(prod_id)+" \n"
                        "AND t1.value <> 'NULL' \n"
                        "AND t1.value <> '/' \n"
                        "AND t1.value <> 'no_selection' \n"
                        "ORDER BY entity_id ASC")
                    cursor.execute(q_attrs)
                    attrs = cursor.fetchall()
                    for a in attrs:
                        if a[0] <> None:
                            if a[0] == 'Modelo' and a[1] <> None:
                                prod_modelo_tec = a[1]
                            elif a[1] <> None:
                                prod_description_sale += codecs.encode(a[1],'utf8')+'; '
                                
                    # Obtener ID de categoria del Producto en Magento
                    prod_mage_categ_id = id_root_category
                    q_categ = ("SELECT category_id FROM mage_catalog_category_product WHERE product_id="+str(prod_id))
                    cursor.execute(q_categ)
                    categories = cursor.fetchall()
                    for c in categories:
                        if c[0] <> None:
                            prod_mage_categ_id = c[0]
                            
                    # Relacion categoria Magento en OpenERP
                    src_product_category = obj_product_category.search(cr, uid, [('mage_categ_id', '=', prod_mage_categ_id)])
                    if src_product_category:
                        id_product_category = obj_product_category.browse(cr, uid, src_product_category[0], context)['id']
                    else:
                        src_product_category = obj_product_category.search(cr, uid, [('mage_categ_id', '=', id_root_category)])
                        id_product_category = obj_product_category.browse(cr, uid, src_product_category[0], context)['id']
                        
                    # Obtener el estatus del producto en Magento
                    q_status = ("SELECT t2.value FROM mage_eav_attribute AS t1 \n"
                        "INNER JOIN mage_catalog_product_entity_int AS t2 \n"
                        "WHERE t2.entity_id = "+str(prod_id)+" \n"
                        "AND t1.attribute_code = 'status' \n"
                        "AND t1.attribute_id = t2.attribute_id")
                    cursor.execute(q_status)
                    status = cursor.fetchall()
                    for s in status:
                        if s[0] == 1:
                            prod_active_in_magento = True
                        else:
                            prod_active_in_magento = False
                        
                    # Manipulacion de imagenes
                    prod_image_url = urllib.urlopen(mage_url+'media/catalog/product'+str(p[15]))
                    if prod_image_url:
                        prod_image = base64.encodestring(prod_image_url.read())
                        prod_image_url.close()
                        q_image_update = "UPDATE product_product SET image='"+prod_image+"',image_small='"+prod_image+"',image_medium='"+prod_image+"' WHERE mage_product_id="+str(prod_id)
                        cr.execute(q_image_update)
                    
                    # Valores para llenar en OpenERP
                    valores = {
                        'mage_product_id': prod_id,
                        'name': prod_name,
                        'name_template': prod_name,
                        'default_code': prod_sku,
                        'description': prod_short_description,
                        'short_description': prod_short_description,
                        'magento_product_type': prod_type,
                        'list_price': prod_price,
                        'mage_url_key': prod_url_key,
                        'mage_url_path': prod_url_path,
                        'modelo_tec': prod_modelo_tec,
                        'description_sale': prod_description_sale,
                        'mage_categ_id': prod_mage_categ_id,
                        'categ_id': id_product_category,
                        'active_in_magento': prod_active_in_magento
                    }
                    
                    # Limpiar variables temporales
                    prod_id = ''
                    prod_name = ''
                    prod_sku = ''
                    prod_short_description = ''
                    prod_type = ''
                    prod_price = ''
                    prod_url_key = ''
                    prod_url_path = ''
                    prod_description_sale = ''
                    prod_modelo_tec = ''
                    prod_mage_categ_id = ''
                    prod_image = ''
                    prod_active_in_magento = ''
                    
                    # Cargar datos en base OpenERP
                    res = obj_product_product.create(cr, uid, valores, context)
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return res
    
    # 16/07/2015 (felix) Metodo para transferir informacion de ventas de Magento a OpenERP
    def trans_sales_magento_openerp(self, cr, uid, ids, context=None):
        # Datos de instancia web
        id_root_category = self.browse(cr, uid, ids[0], context)['magento_root_category_id']
    
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
    
        #cnx = mysql.connector.connect(user='root', password='qBg#@kme@#$r', host='127.0.0.1', database='nordamx_store')
        cnx = mysql.connector.connect(user=str(mage_user),password='qBg#@kme@#$r',host=str(mage_host),database=str(mage_db))
        if not cnx:
            raise osv.except_osv('Advertencia','No se produjo conexion')
            return {}
        cursor = cnx.cursor()
        if cursor:
            # Disposicion de tablas en OpenERP
            obj_product_product = self.pool.get('product.product')
            obj_product_template = self.pool.get('product.template')
            obj_res_partner = self.pool.get('res.partner')
            obj_sale_order = self.pool.get('sale.order')
            obj_sale_order_line = self.pool.get('sale.order.line')
            obj_product_pricelist = self.pool.get('product.pricelist')            
                        
            #####################################################################
            # Tomar y cargar ventas y sus respectivos atributos
            #####################################################################
            q_orders = ("SELECT entity_id,increment_id,customer_id,created_at,state FROM mage_sales_flat_order ORDER BY entity_id ASC")
            cursor.execute(q_orders)
            orders = cursor.fetchall()
            for so in orders:
                if so[0] <> None and so[4] in ['processing','new']:
                    orders_result = []
                    orders_lines_result = []
                    so_mage_order_id = so[0]
                    so_mage_order_ref = so[1]
                    so_mage_id_customer = so[2]
                    so_mage_date_order = so[3]
                    
                    # Obtener datos del cliente
                    src_res_partner = obj_res_partner.search(cr, uid, [('mage_id_customer','=',so_mage_id_customer)])
                    if src_res_partner:
                        id_customer = obj_res_partner.browse(cr, uid, src_res_partner[0], context)['id']
                    else:
                        id_customer = self._create_new_customer(cr, uid, so_mage_id_customer, context)
                    
                    if id_customer <> 0:
                        # Obtener dato de Tarifa (Divisa)
                        src_product_pricelist = obj_product_pricelist.search(cr, uid, [('name','like','Dolares'),('type','=','sale')])
                        id_pricelist = obj_product_pricelist.browse(cr, uid, src_product_pricelist[0], context)['id']
                        
                        # Datos de pedido de venta
                        so_values = {
                            'mage_order_id': so_mage_order_id,
                            'mage_order_ref': so_mage_order_ref,
                            'partner_id': id_customer,
                            'date_order': so_mage_date_order,
                            'partner_invoice_id': id_customer,
                            'partner_shipping_id': id_customer,
                            'order_policy': 'picking',
                            'picking_policy': 'one',
                            'pricelist_id': id_pricelist,
                            'shop_id': 1,
                            'state': 'draft'
                        }
                        order_id = obj_sale_order.create(cr, uid, so_values, context)
                        
                        # Obtener datos especificos de venta, productos, cantidad, precios, impuestos para linea de producto
                        q_so_lines = ("SELECT product_id,qty_ordered,base_price,tax_percent,discount_percent, \n"
                            "sku,name,product_type,price \n"
                            "FROM mage_sales_flat_order_item WHERE order_id="+str(so_mage_order_id))
                        cursor.execute(q_so_lines)
                        order_lines = cursor.fetchall()
                        for so_lines in order_lines:
                            if so_lines[0] <> None:
                                mage_product_id = so_lines[0]
                                mage_cant_prod = so_lines[1]
                                mage_price = so_lines[2]
                                mage_tax_percent = so_lines[3]
                                mage_discount_percent = so_lines[4]
                                mage_sku = so_lines[5]
                                mage_name = so_lines[6]
                                mage_product_type = so_lines[7]
                                
                                # Comparar y obtener datos del product de Magento en OpenERP
                                src_product_product = obj_product_product.search(cr, uid, [('mage_product_id','=',mage_product_id)])
                                if src_product_product:
                                    for prod in obj_product_product.browse(cr, uid, src_product_product, context):
                                        product_id = prod['id']
                                        name = prod['description_sale']
                                        purchase_price = prod['standard_price']
                                else:
                                    product_id = self._create_new_product(cr, uid, mage_product_id, context)
                                        
                                # Obtener ID de impuesto en OpenERP dependiendo del impuesto que viene de Magento
                                tax_amount = mage_tax_percent / 100
                                obj_account_tax = self.pool.get('account.tax')
                                src_account_tax = obj_account_tax.search(cr, uid, [('amount','=',tax_amount)])
                                tax_id = obj_account_tax.browse(cr, uid, src_account_tax[0], context)['id']
                                
                                # Obtener ID de unidad "Unidad(es)"
                                obj_product_uom = self.pool.get('product.uom')
                                src_product_uom = obj_product_uom.search(cr, uid, [('name','=','Unit(s)')])
                                product_uom_id = obj_product_uom.browse(cr, uid, src_product_uom[0], context)['id']
                                
                                # Datos de productos en un pedido de venta Magento
                                so_values_lines = {
                                    'product_id': product_id,
                                    'name': name,
                                    'product_uom_qty': mage_cant_prod,
                                    'product_uos_qty': mage_cant_prod,
                                    'product_uom': product_uom_id,
                                    'price_unit': mage_price,
                                    'purchase_price': purchase_price,
                                    'tax_id': tax_id,
                                    'discount': mage_discount_percent,
                                    'mage_order_id': so_mage_order_id,
                                    'order_id': order_id,
                                    'state': 'draft',
                                    'type': 'make_to_order',
                                    'delay': 0.00
                                }
                                if product_id <> 0:
                                    cr.execute("INSERT INTO sale_order_line (product_id,name,product_uom_qty,product_uos_qty,product_uom,price_unit,\n"
                                        "purchase_price,discount,mage_order_id,order_id,state,type,delay)"
                                        "VALUES ("+str(product_id)+",'"+name+"',"+str(mage_cant_prod)+","+str(mage_cant_prod)+","+str(product_uom_id)+",\n"
                                        ""+str(mage_price)+","+str(purchase_price)+","+str(mage_discount_percent)+","+str(so_mage_order_id)+","+str(order_id)+",\n"
                                        "'draft','make_to_order',"+str(0.00)+")")
                            
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return True
                
    
magento_instance_website_ndk()
    
