# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.translate import _


class FieldMapping(models.Model):

    _name = 'product_import_vendor_cart.field_mapping'
    _rec_name = 'column_name'

    column_name = fields.Char('Column Name in CSV/Excel')
    product_field_id = fields.Many2one('ir.model.fields', 'Product Field', domain=[('model_id.model', '=', 'product.product')])
    vendor_settings_id = fields.Many2one('product_import_vendor_cart.vendor_settings', 'Parent Vendor Settings')
