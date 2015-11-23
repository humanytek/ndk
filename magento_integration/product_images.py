# -*- encoding: utf-8 -*-
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

from osv import osv, fields
from tools.translate import _
import base64, urllib

class product_images(osv.osv):
    _name = "product.images"
    _description = 'Product Images'
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res
    
    _columns = {
        'name':fields.char('Image Title', size=128, required=True),
        'link':fields.boolean('Link?', help="Images can be linked from files on your file system or remote (Preferred)"),
        'filename':fields.char('File Location', size=256),
        'preview':fields.function(_get_image, type="binary", method=True),
        'comments':fields.text('Comments'),
        'product_id':fields.many2one('product.product', 'Product'),
        'base_image':fields.boolean('Base Image'),
        'small_image':fields.boolean('Small Image'),
        'thumbnail':fields.boolean('Thumbnail'),
        'exclude':fields.boolean('Exclude'),
        'position':fields.integer('Position'),
        'sync_status':fields.boolean('Sync Status', readonly=True),
        'create_date': fields.datetime('Created date', readonly=True),
        'write_date': fields.datetime('Updated date', readonly=True),
    }
    _defaults = {
        'link': lambda *a: True,
        'sync_status':lambda * a: False,
        'base_image':lambda * a:True,
        'small_image':lambda * a:True,
        'thumbnail':lambda * a:True,
        'exclude':lambda * a:False
    }
    
    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['link', 'filename', 'image'])
        if each['link']:
            try:
                (filename, header) = urllib.urlretrieve(each['filename'])
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
                
            except:
                img = ''
        else:
            img = each['image']
        return img
    
    def get_changed_ids(self, cr, uid, start_date=False):
        proxy = self.pool.get('product.images')
        domain = start_date and ['|', ('create_date', '>', start_date), ('write_date', '>', start_date)] or []
        return proxy.search(cr, uid, domain)
     
    def del_image_name(self, cr, uid, id, context=None):
        if context is None: context = {}
        image_ext_name_obj = self.pool.get('product.images.external.name')
        name_id = image_ext_name_obj.search(cr, uid, [('image_id', '=', id), ('external_referential_id', '=', context['referential_id'])], context=context)
        if name_id:
            return image_ext_name_obj.unlink(cr, uid, name_id, context=context)
        return False

product_images()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: