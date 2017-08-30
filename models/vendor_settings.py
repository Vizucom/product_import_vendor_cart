# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import csv
import StringIO
import base64
import xlrd


class VendorSettings(models.Model):

    _name = 'product_import_vendor_cart.vendor_settings'

    _FILE_FORMATS = [('csv', 'CSV'),
                     ('excel', 'Excel')]

    _ENCODINGS = [('UTF-8', 'UTF-8'),
                  ('latin_1', 'ISO-8859-1')]

    def get_csv_reader(self, delimiter=','):
        decoded_csv = base64.b64decode(self.sample_file)
        reader = csv.reader(StringIO.StringIO(decoded_csv), delimiter=delimiter)
        return reader

    def get_xls_reader(self):
        decoded_xls = base64.b64decode(self.sample_file)
        filelike = StringIO.StringIO(decoded_xls)
        reader = xlrd.open_workbook(file_contents=filelike.getvalue())
        return reader

    @api.one
    def load_mapping_fields_from_file(self):

        mapping_model = self.env['product_import_vendor_cart.field_mapping']

        if not self.sample_file:
            raise exceptions.except_orm('Error', 'Please give a sample file first')

        self.field_mapping_ids = [(6, 0, [])]

        # Iterate through the columns of the first row, and add them as field mapping rows
        column_number = 1
        if self.file_format == 'csv':
            try:
                reader = self.get_csv_reader(delimiter=str(self.delimiter))
                header_row = next(reader, None)
                encoding = self.encoding

                for column in header_row:
                    mapping_model.create({
                        'column_number': column_number,
                        'column_name': column.decode(encoding),
                        'vendor_settings_id': self.id,
                    })
                    column_number += 1
            except:
                raise exceptions.except_orm('Error', 'Please give a valid CSV file')
        else:
            try:
                reader = self.get_xls_reader()
                sheet = reader.sheet_by_index(0)
                header_row = sheet.row(self.row_with_headers - 1)

                for id, cell_obj in enumerate(header_row):
                    mapping_model.create({
                        'column_number': column_number,
                        'column_name': cell_obj.value,
                        'vendor_settings_id': self.id,
                    })
                    column_number += 1
            except:
                raise exceptions.except_orm('Error', 'Please give a valid XLS file')

        # Delete the sample file
        self.sample_file = False

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner', 'Vendor', domain=[('supplier', '=', True)])
    sample_file = fields.Binary('Sample file', attachment=True)
    sample_image = fields.Binary('Sample image', attachment=True)
    row_with_headers = fields.Integer('Row that contains the headers', default=1)
    stop_after_empty_row = fields.Boolean('Stop after first empty row', help='''For files that contain also other contents than just shopping cart lines''')
    file_format = fields.Selection(_FILE_FORMATS, string='File format')
    delimiter = fields.Char('Delimiter', size=1, default=',')
    encoding = fields.Selection(_ENCODINGS, 'Encoding', default='UTF-8')
    identifying_field_id = fields.Many2one('ir.model.fields', string='Identifying Product Field', domain=[('model_id.model', '=', 'product.product'), ('ttype', 'in', ['char', 'text', 'integer', 'float'])], help='''If this field matches, the existing product is updated instead of creating a new one''')
    field_mapping_ids = fields.One2many('product_import_vendor_cart.field_mapping', 'vendor_settings_id', 'Field Mappings')
    uom_mapping_ids = fields.One2many('product_import_vendor_cart.uom_mapping', 'vendor_settings_id', 'UoM Mappings')
    currency_mapping_ids = fields.One2many('product_import_vendor_cart.currency_mapping', 'vendor_settings_id', 'Currency Mappings')
