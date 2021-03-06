# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.report import report_sxw

class pickingparser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(pickingparser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'get_product_total_qty': self.get_product_total_qty,
        })

    def get_product_total_qty(self, move_lines):
        total_qty = 0.0
        for line in move_lines:
            total_qty += line.product_qty
        return str(total_qty) + ' ' + line.product_uom.name

    def get_product_desc(self, move_line):
        print "called==get_product_desc"
        desc = move_line.product_id.modelo_tec
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

report_sxw.report_sxw('report.stock.picking.out',
                          'stock.picking.out',
                          'addons/hmtk_cybrosys_format_pdf_do/report/picking.rml',
                          parser=pickingparser)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
