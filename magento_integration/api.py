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

from magento.api import API

class Core(API):
    """
    This API extends the API for the custom API implementation
    for the magento extension
    """

    __slots__ = ()

    def websites(self):
        """
        Returns list of all websites
        """
        return self.call('ol_websites.list', [])

    def stores(self, filters=None):
        """
        Returns list of all group store

        :param filters: Dictionary of filters.

               Format :
                   {<attribute>:{<operator>:<value>}}
               Example :
                   {'website_id':{'=':'1'}}
        :return: List of Dictionaries
        """
        return self.call('ol_groups.list', [filters])

    def store_views(self, filters=None):
        """
        Returns list of all store views

        :param filters: Dictionary of filters.

               Format :
                   {<attribute>:{<operator>:<value>}}
               Example :
                   {'website_id':{'=':'1'}}
        :return: List of Dictionaries
        """
        return self.call('ol_storeviews.list', [filters])


class OrderConfig(API):
    '''
    Getting Order Configuration from magento.
    '''

    def get_states(self):
        """
        Get states of orders

        :return: dictionary of all states.
                 Format :
                    {<state>: <state title>}
                 Example :
                    {   'canceled': 'Canceled',
                        'closed': 'Closed',
                        'holded': 'On Hold',
                        'pending_payment': 'Pending Payment'
                    }
        """
        sample_dict = {
                        'canceled': 'canceled',
                        'closed': 'closed',
                        'complete':'complete',
                        #'fraud':'payment_review',
                        'holded':'holded',
                        'payment_review': 'payment_review',
                        'new': 'pending',
                        'pending': 'pending',
                        #'pending_amazon': 'pending_payment',
                        'pending_payment': 'pending_payment',
                        'processing': 'processing',
                        'processing': 'manual',
                      }
        #return self.call('sales_order.status', [])
        return sample_dict

    def get_shipping_methods(self):
        """
        Get available shipping methods.

        :return: List of dictionaries of all available shipping method.
                 Example :
                         [
                            {'code': 'flatrate', 'label': 'Flat Rate'},
                            {'code': 'tablerate', 'label': 'Best Way'},
                            ...
                         ]
        """
        return self.call('sales_order.shipping_methods', [])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: