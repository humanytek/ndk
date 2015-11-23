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

import xmlrpclib
import socket

import magento
from openerp.osv import osv
from openerp.tools.translate import _

class TestConnection(osv.TransientModel):
    _name = 'magento.instance.test_connection'
    _description = 'Test Magento Connection'

    def default_get(self, cursor, user, fields, context):
        """Set a default state

        :param cursor: Database cursor
        :param user: ID of current user
        :param fields: List of fields on wizard
        :param context: Application context
        """
        self.test_connection(cursor, user, context)
        return {}

    def test_connection(self, cursor, user, context):
        """Test the connection to magento instance(s)

        :param cursor: Database cursor
        :param user: ID of current user
        :param context: Application context
        """
        Pool = self.pool

        instance_obj = Pool.get('magento.instance')

        instance = instance_obj.browse(
            cursor, user, context.get('active_id'), context
        )
        try:
            with magento.API(
                instance.url, instance.api_user, instance.api_key
            ):
                return
        except (
            xmlrpclib.Fault, IOError,
            xmlrpclib.ProtocolError, socket.timeout
        ):
            raise osv.except_osv(
                _('Incorrect API Settings!'),
                _('Please check and correct the API settings on instance.')
            )

TestConnection()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: