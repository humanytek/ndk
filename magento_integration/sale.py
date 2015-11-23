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

import magento
from openerp.osv import fields, osv
from openerp.tools.translate import _

class MagentoOrderState(osv.Model):
    """Magento - OpenERP Order State map

    This model stores a map of order states between OpenERP and Magento.
    This allows the user to configure the states mapping according to his/her
    convenience. This map is used to process orders in OpenERP when they are
    imported. This is also used to map the order status on magento when
    sales are exported. This also allows the user to determine in which state
    he/she wants the order to be imported in.
    """
    _name = 'magento.order_state'
    _description = 'Magento - OpenERP Order State map'

    _columns = dict(
        name=fields.char('Name', required=True, size=128, readonly=True),
        code=fields.char('Code', required=True, size=128, readonly=True),
        openerp_state=fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done')
        ], 'OpenERP State'),
        use_for_import=fields.boolean('Import orders in this magento state'),
        instance=fields.many2one(
            'magento.instance', 'Magento Instance', required=True,
            ondelete='cascade',
        )
    )

    _defaults = dict(
        use_for_import=lambda *a: 1,
    )

    _sql_constraints = [
        (
            'code_instance_unique', 'unique(code, instance)',
            'Each magento state must be unique by code in an instance'
        ),
    ]

    def create_all_using_magento_data(
        self, cursor, user, magento_data, context
    ):
        """This method expects a dictionary in which the key is the state
        code on magento and value is the state name on magento.
        This method will create each of the item in the dict as a record in
        this model.

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_data: Magento data in form of dict
        :param context: Application context
        :return: List of browse records of records created
        """
        new_records = []
        default_order_states_map = {
            # 'sent' here means quotation state, thats an OpenERP fuck up.
            'new': 'draft',
            'canceled': 'cancel',
            'closed': 'done',
            'complete': 'done',
            'processing': 'progress',
            'holded': 'waiting_date',
            'pending_payment': 'waiting_date',
            'payment_review': 'waiting_date',
            'pending': 'draft',
            'processing': 'manual',
        }

        for code, name in magento_data.iteritems():
            if self.search(cursor, user, [
                ('code', '=', code),
                ('instance', '=', context['magento_instance'])
            ], context=context):
                continue

            new_records.append(
                self.create(cursor, user, {
                    'name': name,
                    'code': code,
                    'instance': context['magento_instance'],
                    'openerp_state': default_order_states_map[code],
                }, context=context)
            )

        return self.browse(
            cursor, user, new_records, context=context
        )


class SaleLine(osv.osv):
    _inherit = 'sale.order.line'
    _description = "Sale Line" 

    _columns = dict(
        magento_notes=fields.text("Magento Notes"),
    )


class Sale(osv.Model):
    _inherit = 'sale.order'
    _description = "Sale" 

    _columns = dict(
        magento_id=fields.integer('Magento ID', readonly=True),
        magento_instance=fields.many2one(
            'magento.instance', 'Magento Instance', readonly=True,
        ),
        magento_store_view=fields.many2one(
            'magento.store.store_view', 'Store View', readonly=True,
        ),
    )

    _sql_constraints = [(
        'magento_id_instance_unique', 'unique(magento_id, magento_instance)',
        'A sale must be unique in an instance'
    )]

    def check_store_view_instance(self, cursor, user, ids, context=None):
        """
        Checks if instance of store view is same as instance of sale order

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: IDs of records
        :param context: Application context
        :return: True or False
        """
        for sale in self.browse(cursor, user, ids, context=context):
            if sale.magento_id:
                if sale.magento_store_view.instance != sale.magento_instance:
                    return False
        return True

    _constraints = [
        (
            check_store_view_instance,
            'Error: Store view must have same instance as sale order',
            []
        )
    ]

    def find_or_create_using_magento_data(
        self, cursor, user, order_data, context
    ):
        """
        Find or Create sale using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        :returns: Browse record of sale order found/created
        """
        sale = self.find_using_magento_data(
            cursor, user, order_data, context
        )
        if not sale:
            sale = self.create_using_magento_data(
                cursor, user, order_data, context
            )

        return sale

    def find_using_magento_data(
        self, cursor, user, order_data, context
    ):
        """
        Create sale using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        :returns: Browse record of sale order found
        """
        # each sale has to be unique in an instance of magento
        sale_ids = self.search(cursor, user, [
            ('magento_id', '=', int(order_data['order_id'])),
            ('magento_instance', '=', context.get('magento_instance'))
        ], context=context)

        return sale_ids and self.browse(
            cursor, user, sale_ids[0], context
        ) or None

    def find_or_create_using_magento_increment_id(
        self, cursor, user, order_increment_id, context
    ):
        """
        Finds or create sale order using magento ID

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_increment_id: Order increment ID from magento
        :type order_increment_id: string
        :param context: Application context
        :returns: Browse record of sale order created/found
        """
        instance_obj = self.pool.get('magento.instance')

        sale = self.find_using_magento_increment_id(
            cursor, user, order_increment_id, context
        )

        if not sale:
            instance = instance_obj.browse(
                cursor, user, context['magento_instance'], context=context
            )

            with magento.Order(
                instance.url, instance.api_user, instance.api_key
            ) as order_api:
                order_data = order_api.info(order_increment_id)

            sale = self.create_using_magento_data(
                cursor, user, order_data, context
            )

        return sale

    def find_using_magento_id(self, cursor, user, order_id, context):
        """
        Create sale using magento id

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_id: Order ID from magento
        :type order_id: integer
        :param context: Application context
        :returns: Browse record of sale order created
        """
        # each sale has to be unique in an instance of magento
        sale_ids = self.search(cursor, user, [
            ('magento_id', '=', order_id),
            ('magento_instance', '=', context.get('magento_instance'))
        ], context=context)
        return sale_ids and self.browse(
            cursor, user, sale_ids[0], context
        ) or None

    def find_using_magento_increment_id(
        self, cursor, user, order_increment_id, context
    ):
        """
        Create sale using magento id

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_increment_id: Order Increment ID from magento
        :type order_increment_id: string
        :param context: Application context
        :returns: Browse record of sale order created
        """
        instance_obj = self.pool.get('magento.instance')

        instance = instance_obj.browse(
            cursor, user, context['magento_instance'], context=context
        )

        # Each sale has to be unique in an instance of magento
        sale_ids = self.search(cursor, user, [
            ('name', '=', instance.order_prefix + order_increment_id),
            ('magento_instance', '=', context['magento_instance'])
        ], context=context)

        return sale_ids and self.browse(
            cursor, user, sale_ids[0], context
        ) or None

    def create_using_magento_data(self, cursor, user, order_data, context):
        """
        Create a sale order from magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        :returns: Browse record of sale order created
        """
        currency_obj = self.pool.get('res.currency')
        store_view_obj = self.pool.get('magento.store.store_view')
        partner_obj = self.pool.get('res.partner')

        store_view = store_view_obj.browse(
            cursor, user, context['magento_store_view'], context
        )
        if not store_view.shop:
            raise osv.except_osv(
                _('Not Found!'),
                _(
                    'Magento Store %s should have a shop configured.'
                    % store_view.store.name
                )
            )
        if not store_view.shop.pricelist_id:
            raise osv.except_osv(
                _('Not Found!'),
                _(
                    'Shop on store %s does not have a pricelist!'
                    % store_view.store.name
                )
            )

        instance = store_view.instance

        currency = currency_obj.search_using_magento_code(
            cursor, user, order_data['order_currency_code'], context
        )
        if order_data['customer_id']:
            partner = partner_obj.find_or_create_using_magento_id(
                cursor, user, order_data['customer_id'], context
            )
        else:
            partner = partner_obj.create_using_magento_data(
                cursor, user, {
                    'firstname': order_data['customer_firstname'],
                    'lastname': order_data['customer_lastname'],
                    'email': order_data['customer_email'],
                    'magento_id': 0
                },
                context
            )

        partner_invoice_address = \
            partner_obj.find_or_create_address_as_partner_using_magento_data(
                cursor, user, order_data['billing_address'], partner, context
            )

        partner_shipping_address = \
            partner_obj.find_or_create_address_as_partner_using_magento_data(
                cursor, user, order_data['shipping_address'], partner, context
            )

        sale_data = {
            'name': instance.order_prefix + order_data['increment_id'],
            'shop_id': store_view.shop.id,
            'date_order': order_data['created_at'].split()[0],
            'partner_id': partner.id,
            'pricelist_id': store_view.shop.pricelist_id.id,
            'currency_id': currency.id,
            'partner_invoice_id': partner_invoice_address.id,
            'partner_shipping_id': partner_shipping_address.id,
            'magento_id': int(order_data['order_id']),
            'magento_instance': instance.id,
            'magento_store_view': store_view.id,
            'order_line': self.get_item_line_data_using_magento_data(
                cursor, user, order_data, context
            )
        }

        if float(order_data.get('shipping_amount')):
            sale_data['order_line'].append(
                self.get_shipping_line_data_using_magento_data(
                    cursor, user, order_data, context
                )
            )

        if float(order_data.get('discount_amount')):
            sale_data['order_line'].append(
                self.get_discount_line_data_using_magento_data(
                    cursor, user, order_data, context
                )
            )

        sale_id = self.create(
            cursor, user, sale_data, context=context
        )

        sale = self.browse(cursor, user, sale_id, context)

        # Process sale now
        self.process_sale_using_magento_state(
            cursor, user, sale, order_data['state'], context
        )

        return sale

    def get_item_line_data_using_magento_data(
        self, cursor, user, order_data, context
    ):
        """Make data for an item line from the magento data.
        This method decides the actions to be taken on different product types

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        :return: List of data of order lines in required format
        """
        website_obj = self.pool.get('magento.instance.website')
        product_obj = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')

        line_data = []
        for item in order_data['items']:
            if not item['parent_item_id']:
                # If its a top level product, create it
                values = {
                    'name': item['name'],
                    'price_unit': float(item['price']),
                    'product_uom':
                        website_obj.get_default_uom(
                            cursor, user, context
                        ).id,
                    'product_uom_qty': float(item['qty_ordered']),
                    'magento_notes': item['product_options'],
                    'type': 'make_to_order',
                    'product_id':
                        product_obj.find_or_create_using_magento_id(
                            cursor, user, item['product_id'],
                            context=context
                        ).id
                }
                line_data.append((0, 0, values))

            # If the product is a child product of a bundle product, do not
            # create a separate line for this.
            if 'bundle_option' in item['product_options'] and \
                    item['parent_item_id']:
                continue

        # Handle bundle products.
        # Find/Create BoMs for bundle products
        # If no bundle products exist in sale, nothing extra will happen
        bom_obj.find_or_create_bom_for_magento_bundle(
            cursor, user, order_data, context
        )

        return line_data

    def get_shipping_line_data_using_magento_data(
        self, cursor, user, order_data, context
    ):
        """
        Create a shipping line for the given sale using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        """
        website_obj = self.pool.get('magento.instance.website')

        return (0, 0, {
            'name': 'Magento Shipping',
            'price_unit': float(order_data.get('shipping_amount', 0.00)),
            'product_uom':
                website_obj.get_default_uom(
                    cursor, user, context
                ).id,
            'magento_notes': ' - '.join([
                order_data['shipping_method'],
                order_data['shipping_description']
            ])
        })

    def get_discount_line_data_using_magento_data(
        self, cursor, user, order_data, context
    ):
        """
        Create a discount line for the given sale using magento data

        :param cursor: Database cursor
        :param user: ID of current user
        :param order_data: Order Data from magento
        :param context: Application context
        """
        website_obj = self.pool.get('magento.instance.website')

        return (0, 0, {
            'name': order_data['discount_description'] or 'Magento Discount',
            'price_unit': float(order_data.get('discount_amount', 0.00)),
            'product_uom':
                website_obj.get_default_uom(
                    cursor, user, context
                ).id,
            'magento_notes': order_data['discount_description'],
        })

    def process_sale_using_magento_state(
        self, cursor, user, sale, magento_state, context
    ):
        """Process the sale in openerp based on the state of order
        when its imported from magento

        :param cursor: Database cursor
        :param user: ID of current user
        :param sale: Browse record of sale
        :param magento_state: State on magento the order was imported in
        :param context: Application context
        """
        # TODO: Improve this method for invoicing and shipping etc
        magento_order_state_obj = self.pool.get('magento.order_state')

        state_ids = magento_order_state_obj.search(cursor, user, [
            ('code', '=', magento_state),
            ('instance', '=', context['magento_instance'])
        ])

        if not state_ids:
            raise osv.except_osv(
                _('Order state not found!'),
                _('Order state not found/mapped in OpenERP! '
                  'Please import order states on instance'
                 )
            )

        state = magento_order_state_obj.browse(
            cursor, user, state_ids[0], context=context
        )
        openerp_state = state.openerp_state

        # If order is canceled, just cancel it
        if openerp_state == 'cancel':
            self.action_cancel(cursor, user, [sale.id], context)
            return

        # Order is not canceled, move it to quotation
#         self.action_button_confirm(cursor, user, [sale.id], context)

        if openerp_state in ['closed', 'complete', 'processing']:
            self.action_wait(cursor, user, [sale.id], context)

        if openerp_state in ['closed', 'complete']:
            self.action_done(cursor, user, [sale.id], context)

    def export_order_status_to_magento(self, cursor, user, sale, context):
        """
        Export order status to magento.

        :param cursor: Database cursor
        :param user: ID of current user
        :param sale: Browse record of sale
        :param context: Application context
        :return: Browse record of sale
        """
        if not sale.magento_id:
            return sale
        
        magento_order_state_obj = self.pool.get('magento.order_state')
        instance = sale.magento_store_view.instance

        instance = sale.magento_instance
        if sale.state == 'cancel':
            increment_id = sale.name.split(instance.order_prefix)[1]
            # This try except is placed because magento might not accept this
            # order status change due to its workflow constraints.
            # TODO: Find a better way to do it
            try:
                with magento.Order(
                    instance.url, instance.api_user, instance.api_key
                ) as order_api:
                    order_api.cancel(increment_id)
            except xmlrpclib.Fault, f:
                if f.faultCode == 103:
                    return sale

        # TODO: Add logic for other sale states also
        else:
            magento_state_ids = magento_order_state_obj.search(cursor, user, [('instance','=',instance.id),
                                                                            ('openerp_state','=',sale.state)], context=context)
            if magento_state_ids:
                magento_state = magento_order_state_obj.browse(cursor, user, magento_state_ids[0], context=context).code
                increment_id = sale.name.split(instance.order_prefix)[1]
                with magento.Order(instance.url, instance.api_user, instance.api_key) as order_api:
                    try:
                        order_api.addcomment(increment_id, magento_state, comment=None, notify=False)
                    except Exception, e:
                        raise osv.except_osv(_('Warning!'), _(str(e)))
            
        return sale


class MagentoInstanceCarrier(osv.Model):
    _name = 'magento.instance.carrier'
    _description = "Magento Instance Carrier" 

    _columns = dict(
        code=fields.char("Code", size=128, readonly=True),
        title=fields.char('Title', size=128, readonly=True),
        carrier=fields.many2one('delivery.carrier', 'Carrier'),
        instance=fields.many2one(
            'magento.instance', 'Magento Instance', readonly=True
        ),
    )

    _sql_constraints = [(
        'code_instance_unique', 'unique(code, instance)',
        'Shipping method must be unique in instance'
    )]

    def create_all_using_magento_data(
        self, cursor, user, magento_data, context
    ):
        """
        Creates record for list of carriers sent by magento.
        It creates a new carrier only if one with the same code does not
        exist for this instance.

        :param cursor: Database cursor
        :param user: ID of current user
        :param magento_data: List of Dictionary of carriers sent by magento
        :param context: Application context
        :return: List of Browse record of carriers Created/Found
        """
        carriers = []
        for data in magento_data:
            carrier = self.find_using_magento_data(
                cursor, user, data, context
            )
            if carrier:
                carriers.append(carrier)
            else:
                # Create carrier if not found
                carriers.append(
                    self.create_using_magento_data(
                        cursor, user, data, context
                    )
                )
        return carriers

    def create_using_magento_data(self, cursor, user, carrier_data, context):
        """
         Create record for carrier data sent by magento

        :param cursor: Database cursor
        :param user: ID of current user
        :param carrier_data: Dictionary of carrier sent by magento
        :param context: Application context
        :return: Browse record of carrier created
        """
        carrier_id = self.create(
            cursor, user, {
                'code': carrier_data['code'],
                'title': carrier_data['label'],
                'instance': context['magento_instance'],
            }, context=context
        )

        return self.browse(cursor, user, carrier_id, context)

    def find_using_magento_data(self, cursor, user, carrier_data, context):
        """
        Search for an existing carrier by matching code and instance.
        If found, return its browse record else None

        :param cursor: Database cursor
        :param user: ID of current user
        :param carrier_data: Dictionary of carrier sent by magento
        :param context: Application context
        :return: Browse record of carrier found or None
        """
        carrier_ids = self.search(
            cursor, user, [
                ('code', '=', carrier_data['code']),
                ('instance', '=', context['magento_instance']),
            ], context=context
        )
        return carrier_ids and self.browse(
            cursor, user, carrier_ids[0], context
        ) or None


class CustomerShipment(osv.Model):

    _inherit = 'stock.picking'
    _description = "Customer Shipment" 

    _columns = dict(
        magento_instance=fields.related(
            'sale_id', 'magento_instance', type='many2one',
            relation='magento.instance', string=' Magento Instance',
            readonly=True, store=True
        ),
        magento_store_view=fields.related(
            'sale_id', 'magento_store_view', type='many2one',
            relation='magento.store.store_view', string="Magento Store View",
            readonly=True,
        ),
        # Shipment has a separate increment ID
        magento_increment_id=fields.char(
            "Magento Increment ID", size=128, readonly=True
        ),
        write_date=fields.datetime("Write Date", readonly=True),
        is_tracking_exported_to_magento=fields.boolean(
            "Is Tracking Info Exported To Magento"
        ),
    )

    _defaults = dict(
        is_tracking_exported_to_magento=lambda *a: 0,
    )

    _sql_constraints = [
        (
            'instance_increment_id_unique',
            'UNIQUE(magento_instance, magento_increment_id)',
            'Customer shipment should be unique in magento instance'
        ),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: