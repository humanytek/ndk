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
from ..api import OrderConfig

class ImportCarriers(osv.TransientModel):
    _name = 'magento.instance.import_carriers'
    _description = 'Import Carriers'

    def import_carriers(self, cursor, user, ids, context):
        """
        Imports all the carriers for current instance

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: List of ids of records for this model
        :param context: Application context
        """
        instance_obj = self.pool.get('magento.instance')
        magento_carrier_obj = self.pool.get('magento.instance.carrier')

        instance = instance_obj.browse(
            cursor, user, context.get('active_id')
        )
        context.update({
            'magento_instance': instance.id
        })

        with OrderConfig(
            instance.url, instance.api_user, instance.api_key
        ) as order_config_api:
            mag_carriers = order_config_api.get_shipping_methods()

        magento_carrier_obj.create_all_using_magento_data(
            cursor, user, mag_carriers, context
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: