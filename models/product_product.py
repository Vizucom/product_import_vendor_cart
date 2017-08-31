# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ProductProduct(models.Model):

    _inherit = 'product.template'

    ''' A safety measure for better product matching accuracy when importing: 
    The importer itself strips trailing spaces, but users can still create products 
    manually and copy/paste product codes from e.g. Excel, during which unwanted
    trailing spaces can occur. '''

    @api.model
    def create(self, vals):
        if 'manufacturer_pref' in vals and vals['manufacturer_pref']:
            vals['manufacturer_pref'] = vals['manufacturer_pref'].strip()

        return super(ProductProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'manufacturer_pref' in vals and vals['manufacturer_pref']:
            vals['manufacturer_pref'] = vals['manufacturer_pref'].strip()

        return super(ProductProduct, self).write(vals)