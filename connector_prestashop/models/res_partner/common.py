# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api

from ...unit.backend_adapter import GenericAdapter
from ...backend import prestashop


class ResPartner(models.Model):
    _inherit = 'res.partner'

    prestashop_bind_ids = fields.One2many(
        comodel_name='prestashop.res.partner',
        inverse_name='odoo_id',
        string='PrestaShop Bindings',
    )
    prestashop_address_bind_ids = fields.One2many(
        comodel_name='prestashop.address',
        inverse_name='odoo_id',
        string='PrestaShop Address Bindings',
    )


class PrestashopResRartner(models.Model):
    _name = 'prestashop.res.partner'
    _inherit = 'prestashop.binding.odoo'
    _inherits = {'res.partner': 'odoo_id'}

    _rec_name = 'shop_group_id'

    odoo_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        oldname='openerp_id',
    )
    backend_id = fields.Many2one(
        related='shop_group_id.backend_id',
        comodel_name='prestashop.backend',
        string='PrestaShop Backend',
        store=True,
        readonly=True,
    )
    shop_group_id = fields.Many2one(
        comodel_name='prestashop.shop.group',
        string='PrestaShop Shop Group',
        required=True,
        ondelete='restrict',
    )
    shop_id = fields.Many2one(
        comodel_name='prestashop.shop',
        string='PrestaShop Shop',
    )
    group_ids = fields.Many2many(
        comodel_name='prestashop.res.partner.category',
        relation='prestashop_category_partner',
        column1='partner_id',
        column2='category_id',
        string='PrestaShop Groups',
    )
    date_add = fields.Datetime(
        string='Created At (on PrestaShop)',
        readonly=True,
    )
    date_upd = fields.Datetime(
        string='Updated At (on PrestaShop)',
        readonly=True,
    )
    newsletter = fields.Boolean(string='Newsletter')
    default_category_id = fields.Many2one(
        comodel_name='prestashop.res.partner.category',
        string='PrestaShop default category',
        help="This field is synchronized with the field "
        "'Default customer group' in PrestaShop."
    )
    birthday = fields.Date(string='Birthday')
    company = fields.Char(string='Company')
    prestashop_address_bind_ids = fields.One2many(
        comodel_name='prestashop.address',
        inverse_name='odoo_id',
        string='PrestaShop Address Bindings',
    )


class PrestashopAddress(models.Model):
    _name = 'prestashop.address'
    _inherit = 'prestashop.binding.odoo'
    _inherits = {'res.partner': 'odoo_id'}

    _rec_name = 'backend_id'

    @api.multi
    @api.depends(
        'prestashop_partner_id',
        'prestashop_partner_id.backend_id',
        'prestashop_partner_id.shop_group_id',
        )
    def _compute_backend_id(self):
        for address in self:
            address.backend_id = address.prestashop_partner_id.backend_id.id

    @api.multi
    @api.depends('prestashop_partner_id',
                 'prestashop_partner_id.shop_group_id')
    def _compute_shop_group_id(self):
        for address in self:
            address.shop_group_id = (
                address.prestashop_partner_id.shop_group_id.id)

    odoo_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        oldname='openerp_id',
    )
    date_add = fields.Datetime(
        string='Created At (on PrestaShop)',
        readonly=True,
    )
    date_upd = fields.Datetime(
        string='Updated At (on PrestaShop)',
        readonly=True,
    )
    prestashop_partner_id = fields.Many2one(
        comodel_name='prestashop.res.partner',
        string='PrestaShop Partner',
        required=True,
        ondelete='cascade',
    )
    backend_id = fields.Many2one(
        compute='_compute_backend_id',
        comodel_name='prestashop.backend',
        string='PrestaShop Backend',
        store=True,
    )
    shop_group_id = fields.Many2one(
        compute='_compute_shop_group_id',
        comodel_name='prestashop.shop.group',
        string='PrestaShop Shop Group',
        store=True,
    )
    vat_number = fields.Char('PrestaShop VAT')


class PrestashopManufacturer(models.Model):
    _name = 'prestashop.manufacturer'
    _inherit = 'prestashop.binding.odoo'
    _inherits = {'res.partner': 'odoo_id'}
    _description = 'PrestaShop Manufacturers'

    odoo_id = fields.Many2one(
        comodel_name='res.partner',
        string='Manufacturer',
        required=True,
        ondelete='cascade',
    )
    id_reference = fields.Integer(
        string='Reference ID',
        help="In PrestaShop, carriers can be copied with the same 'Reference "
             "ID' (only the last copied carrier will be synchronized with the "
             "ERP)"
    )
    name_ext = fields.Char(
        string='Name in PrestaShop',
    )
    active_ext = fields.Boolean(
        string='Active in PrestaShop',
    )
    date_add = fields.Datetime(
        string='Created At (on PrestaShop)',
        readonly=True,
    )
    date_upd = fields.Datetime(
        string='Updated At (on PrestaShop)',
        readonly=True,
    )


class Manufacturer(models.Model):
    _inherit = "res.partner"

    prestashop_manufacturer_bind_ids = fields.One2many(
        comodel_name='prestashop.manufacturer',
        inverse_name='odoo_id',
        string='PrestaShop Manufacturer Binding',
    )


@prestashop
class PartnerAdapter(GenericAdapter):
    _model_name = 'prestashop.res.partner'
    _prestashop_model = 'customers'


@prestashop
class PartnerAddressAdapter(GenericAdapter):
    _model_name = 'prestashop.address'
    _prestashop_model = 'addresses'


@prestashop
class ManufacturerAdapter(GenericAdapter):
    _model_name = 'prestashop.manufacturer'
    _prestashop_model = 'manufacturers'

    def search(self, filters=None):
        if filters is None:
            filters = {}
        return super(ManufacturerAdapter, self).search(filters)
