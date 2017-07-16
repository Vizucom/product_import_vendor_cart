# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductImportWizardIssue(models.TransientModel):

    _name = 'product_import_vendor_cart.import_wizard_issue'

    wizard_id = fields.Many2one('product_import_vendor_cart.import_wizard', 'Wizard')
    row = fields.Integer('Row')
    data = fields.Char('Data')
    issue = fields.Char('Issue')
