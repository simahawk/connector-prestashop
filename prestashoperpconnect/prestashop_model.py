# -*- coding: utf-8 -*-
#############################################################################
#
#    Prestashoperpconnect : OpenERP-PrestaShop connector
#    Copyright (C) 2013 Akretion (http://www.akretion.com/)
#    Copyright (C) 2013 Camptocamp SA
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#    @author: Guewen Baconnier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import logging
from datetime import datetime

from openerp.osv import fields, orm


from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.connector as connector
from openerp.addons.connector.session import ConnectorSession
#from .unit.import_synchronizer import import_batch, import_partners_since

_logger = logging.getLogger(__name__)


class prestashop_backend(orm.Model):
    _name = 'prestashop.backend'
    _doc = 'Prestashop Backend'
    _inherit = 'connector.backend'

    _backend_type = 'prestashop'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('1.5', '1.5')]

    _columns = {
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True),
        'location': fields.char('Location'),
        'password': fields.char('Password',
            help='Enter the key of the PrestaShop Webservice'),

        # add a field `auto_activate` -> activate a cron
        'import_partners_since': fields.datetime('Import partners since'),
    }

    def synchronize_metadata(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
#        for backend_id in ids:
#            for model in ('prestashop.shop.group',
#                          'prestashop.shop'):
                # import directly, do not delay because this
                # is a fast operation, a direct return is fine
                # and it is simpler to import them sequentially
#                import_batch(session, model, backend_id)

        return True

    def import_partners_since(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        for backend_record in self.browse(cr, uid, ids, context=context):
            since_date = None
            if backend_record.import_partners_since:
                since_date = datetime.strptime(
                        backend_record.import_partners_since,
                        DEFAULT_SERVER_DATETIME_FORMAT)
#            import_partners_since.delay(session, 'prestashop.res.partner',
#                                        backend_record.id,
#                                        since_date=since_date)

        return True

    def import_customer_groups(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
#        for backend_id in ids:
#            import_batch.delay(session, 'prestashop.res.partner.category',
#                               backend_id)

        return True

    def import_product_categories(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
#        for backend_id in ids:
#            import_batch.delay(session, 'prestashop.product.category',
#                               backend_id)
        return True


class prestashop_binding(orm.AbstractModel):
    _name = 'prestashop.binding'
    _inherit = 'external.binding'
    _description = 'PrestaShop Binding (abstract)'

    _columns = {
        # 'openerp_id': openerp-side id must be declared in concrete model
        'backend_id': fields.many2one(
            'prestashop.backend',
            'PrestaShop Backend',
            required=True,
            ondelete='restrict'),
        # TODO : do I keep the char like in Magento, or do I put a PrestaShop ?
        'prestashop_id': fields.integer('ID on PrestaShop'),
    }

    # the _sql_contraints cannot be there due to this bug:
    # https://bugs.launchpad.net/openobject-server/+bug/1151703



# TODO remove external.shop.group from connector_ecommerce
class prestashop_shop_group(orm.Model):
    _name = 'prestashop.shop.group'
    _inherit = 'prestashop.binding'

    _columns = {
        'name': fields.char('Name', required=True),
        'shop_ids': fields.one2many(
            'prestashop.shop',
            'shop_group_id',
            string="Shops",
            readonly=True),
    }

    _sql_constraints = [
        ('prestashop_uniq', 'unique(backend_id, prestashop_id)',
         'A shop group with the same ID on PrestaShop already exists.'),
    ]


# TODO migrate from sale.shop
class prestashop_shop(orm.Model):
    _name = 'prestashop.shop'
    _inherit = 'prestashop.binding'
    _description = 'PrestaShop Shop'

    _inherits = {'sale.shop': 'openerp_id'}


    def _get_shop_from_shopgroup(self, cr, uid, ids, context=None):
        return self.pool.get('prestashop.shop').search(cr, uid, [('shop_group_id', 'in', ids)], context=context)


    _columns = {
        'shop_group_id': fields.many2one(
            'prestashop.shop.group',
            'PrestaShop Shop Group',
            required=True,
            ondelete='cascade'),
        'openerp_id': fields.many2one(
            'sale.shop',
            string='Sale Shop',
            required=True,
            readonly=True,
            ondelete='cascade'),
        # what is the exact purpose of this field?
        'default_category_id': fields.many2one(
            'product.category',
            'Default Product Category',
            help="The category set on products when?? TODO."
            "\nOpenERP requires a main category on products for accounting."),
        'backend_id': fields.related(
            'shop_group_id', 'backend_id',
            type='many2one',
            relation='prestashop.backend',
            string='PrestaShop Backend',
            store={
                'prestashop.shop': (lambda self, cr, uid, ids, c={}: ids, ['shop_group_id'], 10),
                'prestashop.shop.group': (_get_shop_from_shopgroup, ['backend_id'], 20),
                  },
            readonly=True),
    }

    _sql_constraints = [
        ('prestashop_uniq', 'unique(backend_id, prestashop_id)',
         'A shop with the same ID on PrestaShop already exists.'),
    ]


class sale_shop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'prestashop_bind_ids': fields.one2many(
            'prestashop.shop', 'openerp_id',
            string='PrestaShop Bindings',
            readonly=True),
    }

