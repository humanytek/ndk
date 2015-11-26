from openerp.osv import osv, fields


class StockPicking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'shipping_address': fields.text("Shipping Address"),
    }


class StockPickingOut(osv.osv):
    _inherit = 'stock.picking.out'

    _columns = {
        'shipping_address': fields.text("Shipping Address"),
    }