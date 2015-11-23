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

from openerp.osv import osv
from openerp.tools.translate import _

class ExportShipmentStatus(osv.TransientModel):
    _name = 'magento.store.store_view.export_shipment_status'
    _description = 'Export Shipment Status'

    def export_shipment_status(self, cursor, user, ids, context):
        """
        Exports shipment status for sale orders related to current store view

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        :return: View for shipments exported
        """
        store_view_obj = self.pool.get('magento.store.store_view')

        store_view = store_view_obj.browse(
            cursor, user, context.get('active_id')
        )
        context.update({
            'magento_instance': store_view.instance.id
        })

        shipments = store_view_obj.export_shipment_status_to_magento(
            cursor, user, store_view, context
        )
        return self.open_shipments(cursor, user, map(int, shipments), context)

    def open_shipments(self, cursor, user, shipment_ids, context):
        """
        Open view for Shipments exported

        :param cursor: Database cursor
        :param user: ID of current user
        :param shipment_ids: List of Shipment IDs
        :param context: Application context
        :return: Tree view for shipments
        """
        ir_model_data = self.pool.get('ir.model.data')

        tree_res = ir_model_data.get_object_reference(
            cursor, user, 'stock', 'view_picking_out_tree'
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Shipments with status exported to magento'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'stock.picking.out',
            'views': [(tree_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', shipment_ids)]
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: