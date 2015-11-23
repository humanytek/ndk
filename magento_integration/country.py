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
import pycountry

class Country(osv.osv):
    _inherit = 'res.country'
    _description = 'Country'

    def search_using_magento_code(self, cursor, user, code, context):
        """
        Searches for country with given magento code.

        :param cursor: Database cursor
        :param user: ID of current user
        :param code: ISO code of country
        :param context: Application context
        :return: Browse record of country if found else raises error
        """
        country_ids = self.search(
            cursor, user, [('code', '=', code)], context=context
        )

        if not country_ids:
            raise osv.except_osv(
                _('Not Found!'),
                _('Country with ISO code %s does not exists.' % code)
            )

        country = self.browse(
            cursor, user, country_ids[0], context=context
        )
        return country


class CountryState(osv.Model):
    _inherit = 'res.country.state'
    _description = "Country State"

    def find_or_create_using_magento_region(
        self, cursor, user, country, region, context
    ):
        """
        Looks for the state whose `region` is sent by magento in `country`
        If state already exists, return that else create a new one and
        return

        :param cursor: Database cursor
        :param user: ID of current user
        :param country: Browse record of country
        :param region: Name of state from magento
        :param context: Application context
        :return: Browse record of record created/found
        """
        state = self.find_using_magento_region(
            cursor, user, country, region, context
        )
        if not state:
            state = self.create_using_magento_region(
                cursor, user, country, region, context
            )

        return state

    def find_using_magento_region(
        self, cursor, user, country, region, context
    ):
        """
        Looks for the state whose `region` is sent by magento
        If state already exists, return that

        :param cursor: Database cursor
        :param user: ID of current user
        :param country: Browse record of country
        :param region: Name of state from magento
        :param context: Application context
        :return: Browse record of record found
        """
        state_ids = self.search(
            cursor, user, [
                ('name', 'ilike', region),
                ('country_id', '=', country.id),
            ], context=context
        )

        return state_ids and self.browse(
            cursor, user, state_ids[0], context=context
        ) or None

    def create_using_magento_region(
        self, cursor, user, country, region, context
    ):
        """
        Creates state for the region sent by magento

        :param cursor: Database cursor
        :param user: ID of current user
        :param country: Browse record of country
        :param region: Name of state from magento
        :param context: Application context
        :return: Browse record of record created
        """
        code = None
        try:
            for subdivision in pycountry.subdivisions.get(
                    country_code=country.code):
                if subdivision.name.upper() == region.upper():
                    code = ''.join(list(region)[:3]).upper()
                    break
            if not code:
                if country.code == 'US':
                    code = 'APO'
                else:
                    code = ''.join(list(region)[:3]).upper()
        except KeyError:
            raise osv.except_osv(
                _('Country Not Found!'),
                _('No country found with code %s' % country.code)
            )
        finally:
            state_id = self.create(
                cursor, user, {
                    'name': region,
                    'country_id': country.id,
                    'code': code,
                }, context=context
            )

        return self.browse(cursor, user, state_id, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: