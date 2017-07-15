# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.translate import _


class CurrencyMapping(models.Model):

    _name = 'product_import_vendor_cart.currency_mapping'
    _rec_name = 'value_in_file'

    currency_id = fields.Many2one('res.currency', 'Currency')
    value_in_file = fields.Char('Value in File')
    vendor_settings_id = fields.Many2one('product_import_vendor_cart.vendor_settings', 'Parent Vendor Settings')
