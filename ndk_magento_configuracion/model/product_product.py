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

# Python
import time
import openerp
import codecs
import mysql.connector
import base64, urllib
import logging
_logger = logging.getLogger(__name__)


class product_product_ndk(osv.Model):

    _inherit = 'product.product'
    _description = 'Campos adicionales para tabla product.product'
    _columns = {
        'modelo_tec': fields.text('Modelo'),
        'mage_url_key': fields.char('URL key Magento'),
        'mage_url_path': fields.char('URL path Magento'),
        'mage_product_id': fields.char('ID Product Magento'),
        'mage_categ_id': fields.integer('ID Category')
    }
    _sql_constraints = [
        ('mage_product_id_uniq', 'unique(mage_product_id)', 'Este campo debe ser unico')
    ]
    
    # 08/07/2015 (felix) Metodo para actualizar datos del producto Magento->OpenERP
    def update_prod_magento_openerp(self, cr, uid, ids, context=None):
    
        # Disposicion de tablas en OpenERP
        obj_product_template = self.pool.get('product.template')
        obj_product_category = self.pool.get('product.category')
        obj_product_images = self.pool.get('product.images')
        obj_magento_instance_website = self.pool.get('magento.instance.website')
        
        # Datos de instancia web
        all_magento_instance_website = obj_magento_instance_website.search(cr, uid, [(1,'=',1)], limit=1)
        id_root_category = obj_magento_instance_website.browse(cr, uid, all_magento_instance_website[0], context)['magento_root_category_id']
    
        # ID del producto
        self_product_id = self.browse(cr, uid, ids[0], context)['id']
        mage_product_id = self.browse(cr, uid, ids[0], context)['mage_product_id']
    
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
            prod_description_purchase = ''
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
                    prod_brand = p[10]
                    
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
                                prod_modelo_tec = codecs.encode(a[1],'utf8')
                            elif a[1] <> None:
                                prod_description_sale += codecs.encode(a[1],'utf8')+'; '
                                
                            # 01/10/2015 (felix) Descripcion en ingles
                            if codecs.encode(a[0],'utf8') == 'Descripción en ingles' and a[1] <> None:
                                prod_description_purchase = codecs.encode(a[1],'utf8')
                    
                    # Obtener valores de atributos alternativos venidos de ComboBox de Magento
                    q_attrs_1 = ("SELECT t2.value \n"
                        "FROM mage_catalog_product_entity_int AS t1 \n"
                        "INNER JOIN mage_eav_attribute_option_value AS t2 \n"
                        "ON t1.entity_id = "+str(prod_id)+" \n"
                        "AND t1.value = t2.option_id \n"
                        "AND t1.store_id = t2.store_id \n"
                        "AND t2.value <> 'Female' \n"
                        "AND t2.value <> 'Male' \n"
                        "ORDER BY t2.value_id ASC")
                    cursor.execute(q_attrs_1)
                    attrs_1 = cursor.fetchall()
                    for a in attrs_1:
                        if a[0] <> None:
                            prod_description_sale += codecs.encode(a[0],'utf8')+'; '
                                
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
                        q_image_update = "UPDATE product_product SET image='"+prod_image+"',image_small='"+prod_image+"',image_medium='"+prod_image+"' WHERE mage_product_id LIKE '"+str(prod_id)+"'"
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
                        'description_sale': prod_modelo_tec+'; '+prod_description_sale,
                        'description_purchase': prod_description_purchase,
                        'mage_categ_id': prod_mage_categ_id,
                        'categ_id': id_product_category,
                        'active_in_magento': prod_active_in_magento,
                        'brand': prod_brand
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
                    prod_description_purchase = ''
                    prod_modelo_tec = ''
                    prod_mage_categ_id = ''
                    prod_image = ''
                    prod_active_in_magento = ''
                    
            # Cargar datos en base OpenERP
            for p in prod_result:
                src_product_product = self.search(cr, uid, [('mage_product_id','=',mage_product_id)])
                if src_product_product:
                    id_product_product = self.browse(cr, uid, src_product_product[0], context)['id']
                    self.write(cr, uid, [id_product_product], p, context)
                    
        else:
            cursor.close()
            cnx.close()
            raise osv.except_osv('Advertencia','No hay puntero de base de datos')
            return {}
                        
        cursor.close()
        cnx.close()
        return True
        
    
product_product_ndk()
    
