# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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

import tools
from osv import fields, osv

class sale_report(osv.osv):
    _inherit = "sale.report"
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report')
        cr.execute("""
            drop function if exists get_to_currency_rate(currency_id integer, date_order date);
            CREATE OR REPLACE FUNCTION get_to_currency_rate(x_currency_id integer, x_date_order date)
            RETURNS TABLE(rate numeric) AS
             $BODY$
            DECLARE
               local_currency_id integer := x_currency_id;
               local_date_order date := x_date_order;
            BEGIN
            return query
            select tocu.rate from res_currency_rate tocu where currency_id = local_currency_id and name <= local_date_order ORDER BY name desc LIMIT 1;
             END
            $BODY$
            LANGUAGE 'plpgsql';
            
            drop function if exists get_from_currency_rate(currency_id integer, date_order date);
            CREATE OR REPLACE FUNCTION get_from_currency_rate(x_currency_id integer, x_date_order date)
            RETURNS TABLE(rate numeric) AS
            $BODY$
            DECLARE
               local_currency_id integer := x_currency_id;
               local_date_order date := x_date_order;
            BEGIN
            return query
            select fcu.rate from res_currency_rate fcu where currency_id = local_currency_id and name <= local_date_order ORDER BY name desc LIMIT 1;
             END
            $BODY$
            LANGUAGE 'plpgsql';
            
            create or replace view sale_report as (
                select
                    min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    1 as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    to_char(s.date_order, 'YYYY') as year,
                    to_char(s.date_order, 'MM') as month,
                    to_char(s.date_order, 'YYYY-MM-DD') as day,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.shop_id as shop_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    t.categ_id as categ_id,
                    s.partner_shipping_id,
                    s.partner_shipping_id::integer as partner_shipping_id_qty_1,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    Case When pp.currency_id = cu.id 
                        Then
                           sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0)
                        Else
                           sum(l.product_uom_qty * (l.price_unit *(select get_to_currency_rate(cu.id, s.date_order))/(select get_from_currency_rate(pp.currency_id, s.date_order))) * (100.0-l.discount) / 100.0)    
                     END as price_total
                from
                    sale_order s
                    join sale_order_line l on (s.id=l.order_id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                            left join product_pricelist pp on (s.pricelist_id = pp.id)
                            left join res_company rc on (rc.id = s.company_id)
                            left join res_currency cu on (cu.id = rc.currency_id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                group by
                    l.product_id,
                    l.product_uom_qty,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.shop_id,
                    s.company_id,
                    s.state,
                    s.partner_shipping_id,
                    s.pricelist_id,
                    s.project_id,
                    pp.currency_id,
                    cu.id,
                    s.date_order
            )
        """)
sale_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
