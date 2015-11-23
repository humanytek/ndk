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

import magento
import openerp
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class MagentoWebsitePartner(osv.Model):
    _name = 'magento.website.partner'
    _description = "Magento Website partner store" 

    _columns = dict(
        magento_id=fields.integer('Magento ID', readonly=True),
        website=fields.many2one(
            'magento.instance.website', 'Website', required=True,
            readonly=True,
        ),
        partner=fields.many2one(
            'res.partner', 'Partner', required=True, readonly=True
        )
    )

    def check_unique_partner(self, cursor, user, ids, context=None):
        """Checks thats each partner should be unique in a website if it
        does not have a magento ID of 0. magento_id of 0 means its a guest
        cutsomers.

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: IDs of records
        :param context: Application context
        :return: True or False
        """
        for magento_partner in self.browse(cursor, user, ids, context=context):
            if magento_partner.magento_id != 0 and self.search(cursor, user, [
                ('magento_id', '=', magento_partner.magento_id),
                ('website', '=', magento_partner.website.id),
                ('id', '!=', magento_partner.id),
            ], context=context, count=True) > 0:
                return False
        return True

    _constraints = [
        (
            check_unique_partner,
            'Error: Customers should be unique for a website',
            []
        )
    ]


class Partner(osv.Model):
    _inherit = 'res.partner'
    _description = "Partner" 

    _columns = dict(
        magento_ids=fields.one2many(
            'magento.website.partner', 'partner', "Magento IDs", readonly=True
        ),
    )

    def find_or_create_using_magento_id(
        self, cursor, user, magento_id, context
    ):
        """
        Finds or creates partner using magento ID

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Partner ID sent by magento
        :param context: Application context.
        :return: Browse record of record created/found
        """
        instance_obj = self.pool.get('magento.instance')

        partner = self.find_using_magento_id(cursor, user, magento_id, context)
        if not partner:
            instance = instance_obj.browse(
                cursor, user, context['magento_instance'], context=context
            )

            with magento.Customer(
                instance.url, instance.api_user, instance.api_key
            ) as customer_api:
                customer_data = customer_api.info(magento_id)

            partner = self.create_using_magento_data(
                cursor, user, customer_data, context
            )
        return partner

    def find_using_magento_id(self, cursor, user, magento_id, context):
        """
        Finds partner with magento id

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_id: Partner ID sent by magento
        :param context: Application context.
        :return: Browse record of record found
        """
        magento_partner_obj = self.pool.get('magento.website.partner')

        record_ids = magento_partner_obj.search(
            cursor, user, [
                ('magento_id', '=', magento_id),
                ('website', '=', context['magento_website'])
            ], context=context
        )

        return record_ids and magento_partner_obj.browse(
            cursor, user, record_ids[0], context=context
        ).partner or None

    def find_or_create(self, cursor, user, customer_data, context):
        """
        Looks for the customer whose `customer_data` is sent by magento against
        the `magento_website_id` in context.
        If a record exists for this, return that else create a new one and
        return

        :param cursor: Database cursor
        :param user: ID of current user
        :param customer_data: Dictionary of values for customer sent by magento
        :param context: Application context. Contains the magento_website to
                        which the customer has to be linked
        :return: Browse record of record created/found
        """
        if not context['magento_website']:
            raise osv.except_osv(
                _('Not Found!'),
                _('Website does not exists in context. ')
            )

        partner = self.find_using_magento_data(
            cursor, user, customer_data, context
        )

        if not partner:
            partner = self.create_using_magento_data(
                cursor, user, customer_data, context
            )

        return partner

    def create_using_magento_data(self, cursor, user, customer_data, context):
        """
        Creates record of customer values sent by magento

        :param cursor: Database cursor
        :param user: ID of current user
        :param customer_data: Dictionary of values for customer sent by magento
        :param context: Application context. Contains the magento_website
                        to which the customer has to be linked
        :return: Browse record of record created
        """
        partner_id = self.create(
            cursor, user, {
                'name': u' '.join(
                    [customer_data['firstname'], customer_data['lastname']]
                ),
                'email': customer_data['email'],
                'magento_ids': [
                    (0, 0, {
                        'magento_id': customer_data.get('customer_id', 0),
                        'website': context['magento_website'],
                    })
                ],
            }, context=context
        )

        return self.browse(cursor, user, partner_id, context)

    def find_using_magento_data(self, cursor, user, customer_data, context):
        """
        Looks for the customer whose `customer_data` is sent by magento against
        the `magento_website_id` in context.
        If record exists returns that else None

        :param cursor: Database cursor
        :param user: ID of current user
        :param customer_data: Dictionary of values for customer sent by magento
        :param context: Application context. Contains the magento_website
                        to which the customer has to be linked
        :return: Browse record of record found
        """
        magento_partner_obj = self.pool.get('magento.website.partner')

        # This is a guest customer. Create a new partner for this
        if not customer_data.get('customer_id'):
            return None

        record_ids = magento_partner_obj.search(
            cursor, user, [
                ('magento_id', '=', customer_data['customer_id']),
                ('website', '=', context['magento_website'])
            ], context=context
        )
        return record_ids and magento_partner_obj.browse(
            cursor, user, record_ids[0], context
        ).partner or None

    def find_or_create_address_as_partner_using_magento_data(
        self, cursor, user, address_data, parent, context
    ):
        """Find or Create an address from magento with `address_data` as a
        partner in openerp with `parent` as the parent partner of this address
        partner (how fucked up is that).

        :param cursor: Database cursor
        :param user: ID of current user
        :param address_data: Dictionary of address data from magento
        :param parent: Parent partner for this address partner.
        :param context: Application context.
        :return: Browse record of address created/found
        """
        for address in parent.child_ids + [parent]:
            if self.match_address_with_magento_data(
                cursor, user, address, address_data
            ):
                break
        else:
            address = self.create_address_as_partner_using_magento_data(
                cursor, user, address_data, parent, context
            )

        return address

    def match_address_with_magento_data(
        self, cursor, user, address, address_data
    ):
        """Match the `address` in openerp with the `address_data` from magento
        If everything matches exactly, return True, else return False

        :param cursor: Database cursor
        :param user: ID of current user
        :param address: Browse record of address partner
        :param address_data: Dictionary of address data from magento
        :return: True if address matches else False
        """
        # Check if the name matches
        if address.name != u' '.join(
            [address_data['firstname'], address_data['lastname']]
        ):
            return False

        if not all([
            (address.street or None) == address_data['street'],
            (address.zip or None) == address_data['postcode'],
            (address.city or None) == address_data['city'],
            (address.phone or None) == address_data['telephone'],
            (address.fax or None) == address_data['fax'],
            (address.country_id and address.country_id.code or None) ==
                address_data['country_id'],
            (address.state_id and address.state_id.name or None) ==
                address_data['region']
        ]):
            return False

        return True

    def create_address_as_partner_using_magento_data(
        self, cursor, user, address_data, parent, context
    ):
        """Create a new partner with the `address_data` under the `parent`

        :param cursor: Database cursor
        :param user: ID of current user
        :param address_data: Dictionary of address data from magento
        :param parent: Parent partner for this address partner.
        :param context: Application Context
        :return: Browse record of address created
        """
        country_obj = self.pool.get('res.country')
        state_obj = self.pool.get('res.country.state')

        country = country_obj.search_using_magento_code(
            cursor, user, address_data['country_id'], context
        )
        if address_data['region']:
            state_id = state_obj.find_or_create_using_magento_region(
                cursor, user, country, address_data['region'], context
            ).id
        else:
            state_id = None
        address_id = self.create(cursor, user, {
            'name': u' '.join(
                [address_data['firstname'], address_data['lastname']]
            ),
            'street': address_data['street'],
            'state_id': state_id,
            'country_id': country.id,
            'city': address_data['city'],
            'zip': address_data['postcode'],
            'phone': address_data['telephone'],
            'fax': address_data['fax'],
            'parent_id': parent.id,
        }, context=context)

        return self.browse(cursor, user, address_id, context=context)
    
    def export_customers_to_magento(self, cr, uid, website_id, context=None, use_local_cr=False):
        local_cr = cr
        if use_local_cr:
            db = openerp.sql_db.db_connect(cr.dbname)
            local_cr = db.cursor()
        
        store_obj = self.pool.get('magento.website.store')
        magento_website_partner_obj = self.pool.get('magento.website.partner')
        website_obj = self.pool.get('magento.instance.website')
        
        website = website_obj.browse(local_cr, uid, website_id, context=context)
        instance = website.instance

        customer_ids = self.search(local_cr, uid, [('magento_ids','=',None), ('customer','=',True), ('email','!=',False)], context=context)
        customer_browse = self.browse(local_cr, uid, customer_ids, context=context)
        store_ids = store_obj.search(local_cr, uid, [('instance','=',instance.id)], context=context)
        for customer in customer_browse:
            name_list = customer.name.split(' ')
            fname = lname = name_list and name_list[0] or ''
            if len(name_list) > 1:
                lname = ' '.join(name_list[1:])
            data = {
                    'firstname': fname,
                    'lastname': lname,
                    'store_id': store_ids and store_ids[0] or False,
                    'website_id': website.magento_id,
                    'email': customer.email,
                    }
            
            address_data = {
                            'firstname': fname or False,
                            'lastname': lname or False,
                            'city': customer.city or False,
                            'country_id': customer.country_id and customer.country_id.code or False,
                            'telephone': customer.phone or customer.mobile or False,
                            'street': (customer.street or '')+ '\n' + (customer.street2 or '') or False,
                            'postcode': customer.zip,
                            'region': customer.state_id and customer.state_id.name,
                            }
            
            with magento.Customer(instance.url, instance.api_user, instance.api_key) as customer_api:
                existing_customer = customer_api.list({'email':{'=':customer.email}})
                try:
                    if existing_customer:
                        customer_id = existing_customer[0].get("customer_id", False)
                    else:
                        customer_id = customer_api.create(data)
                    magento_website_partner_obj.create(local_cr, uid, {
                                                                    'magento_id': customer_id,
                                                                    'website': website.id,
                                                                    'partner': customer.id,
                                                                    })
                except Exception, e:
                    _logger.log(logging.WARNING, _(str(e)))
                    #raise osv.except_osv(_('Warning!'), _(str(e)))
                if False not in address_data.values() and not existing_customer:
                    address_data.update({
                                         'fax': customer.fax,
                                         })
                    with magento.CustomerAddress(instance.url, instance.api_user, instance.api_key) as address_api:
                        try:
                            address_api.create(customer_id, address_data)
                        except Exception, e:
                            _logger.log(logging.WARNING, _(str(e)))
                            #raise osv.except_osv(_('Warning!'), _(str(e)))
        if use_local_cr:
            local_cr.commit()
            local_cr.close()
            
        return True
    
Partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: