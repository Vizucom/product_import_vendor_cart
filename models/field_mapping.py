# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools.translate import _


class FieldMapping(models.Model):

    _name = 'product_import_vendor_cart.field_mapping'
    _rec_name = 'column_name'
    _order = 'column_number'

    column_name = fields.Char('Column Name in CSV/Excel')
    column_number = fields.Integer('Column Number')

    product_field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                         relation='mapping_pfield_rel',
                                         column1='mapping_id',
                                         column2='pfield_id',
                                         string='Product Fields',
                                         domain=[('model_id.model', '=', 'product.product'), ('ttype', 'in', ['char', 'text', 'many2one', 'integer', 'float'])])

    supplierinfo_field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                              relation='mapping_sfield_rel',
                                              column1='mapping_id',
                                              column2='sfield_id',
                                              string='Vendor Fields',
                                              domain=[('model_id.model', '=', 'product.supplierinfo'), ('ttype', 'in', ['char', 'text', 'many2one', 'integer', 'float'])])

    vendor_settings_id = fields.Many2one('product_import_vendor_cart.vendor_settings', 'Parent Vendor Settings')
