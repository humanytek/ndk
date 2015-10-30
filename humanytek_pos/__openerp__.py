# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 BroadTech IT Solutions.
#    (http://wwww.broadtech-innovations.com)
#    contact@boradtech-innovations.com
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

{
    'name': 'Humanytek POS',
    'version': '1.0',
    'category': 'Point Of Sale',
    'summary': 'Manage Point of sale activities',
    'description': """
Point of Sale
====================

This module adds support for point of sale activities. Return order functionality from ui.

    """,
    'author': 'Broadtech-innovations',
    'depends': ['point_of_sale'],
    'website': 'http://wwww.broadtech-innovations.com',
    'data': [
             'wizard/user_validation_view.xml',
             'point_of_sale_view.xml',
             'session_report.xml',
             'views/report_session.xml',
             'views/humanytek_pos_files.xml',
        ],
    'qweb': ['static/src/xml/pos.xml'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    

