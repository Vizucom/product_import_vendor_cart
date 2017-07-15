# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.translate import _


class UomMapping(models.Model):

    _name = 'product_import_vendor_cart.uom_mapping'
    _rec_name = 'value_in_file'

    uom_id = fields.Many2one('product.uom', 'UoM')
    value_in_file = fields.Char('Value in File')
    vendor_settings_id = fields.Many2one('product_import_vendor_cart.vendor_settings', 'Parent Vendor Settings')
