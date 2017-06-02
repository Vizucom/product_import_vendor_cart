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

    def get_csv_reader(self):
        decoded_csv = base64.b64decode(self.sample_file)
        reader = csv.reader(StringIO.StringIO(decoded_csv))
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
        if self.file_format == 'csv':
            try:
                reader = self.get_csv_reader()
                header_row = next(reader, None)
                for column in header_row:
                    mapping_model.create({
                        'column_name': column,
                        'vendor_settings_id': self.id,
                    })
            except:
                raise exceptions.except_orm('Error', 'Please give a valid CSV file')
        else:
            try:
                reader = self.get_xls_reader()
                sheet = reader.sheet_by_index(0)
                header_row = sheet.row(self.row_with_headers - 1)

                for id, cell_obj in enumerate(header_row):
                    mapping_model.create({
                        'column_name': cell_obj.value,
                        'vendor_settings_id': self.id,
                    })
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
    field_mapping_ids = fields.One2many('product_import_vendor_cart.field_mapping', 'vendor_settings_id', 'Field Mappings')
