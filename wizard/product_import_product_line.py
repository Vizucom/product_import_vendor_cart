# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductImportProductLine(models.TransientModel):

    _name = 'product_import_vendor_cart.import_product_line'

    name = fields.Char('Product')
    wizard_id = fields.Many2one('product_import_vendor_cart.import_wizard', 'Wizard')
