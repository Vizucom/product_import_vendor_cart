# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import base64
import csv
import StringIO
import logging
import xlrd

_logger = logging.getLogger(__name__)


class ProductImportWizard(models.TransientModel):

    _name = 'product_import_vendor_cart.import_wizard'

    def add_issue(self, row, data, issue):
        ''' Adds a new issue row to the o2m list '''
        issue_model = self.env['product_import_vendor_cart.import_wizard_issue']
        issue_model.create({
            'row': row,
            'data': data,
            'issue': issue,
            'wizard_id': self.id,
        })

    def get_return_dict(self):
        ''' Returning this reopens the wizard '''
        view_id = self.pool['ir.model.data'].xmlid_to_res_id(self._cr, self._uid, 'product_import_vendor_cart.cart_import_form')
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product_import_vendor_cart.import_wizard',
            'res_id': self.id,
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': 'Vendor Shopping Cart Import',
        }

    @api.multi
    def file_select(self):
        ''' Redirect back to CSV upload '''
        self.ensure_one()
        self.state = 'file_selection'
        self.bom_file = False
        self.issue_ids = [(6, 0, [])]
        return self.get_return_dict()

    @api.multi
    def file_validate(self):
        ''' Validate the uploaded CSV before actually importing the data'''
        self.ensure_one()
        self.state = 'validation'
        self.validate_contents()
        return self.get_return_dict()

    @api.multi
    def file_import(self):
        ''' Parse and import CSV data, first the product info and then BOMs '''
        self.ensure_one()
        self.import_products()
        self.state = 'done'
        self.message_done = 'Import completed.'
        return self.get_return_dict()

    def get_csv_reader(self, delimiter):
        decoded_csv = base64.b64decode(self.product_file)
        reader = csv.reader(StringIO.StringIO(decoded_csv), quotechar='"', delimiter=delimiter)
        range_start = 1
        csv_rows = list(reader)
        range_stop = len(csv_rows)
        # List() consumes the reader, so reinitialize for later use
        reader = csv.reader(StringIO.StringIO(decoded_csv), quotechar='"', delimiter=delimiter)
        return reader, range_start, range_stop, csv_rows

    def get_xls_reader(self):
        decoded_xls = base64.b64decode(self.product_file)
        filelike = StringIO.StringIO(decoded_xls)
        reader = xlrd.open_workbook(file_contents=filelike.getvalue())
        sheet = reader.sheet_by_index(0)
        range_start = self.vendor_settings_id.row_with_headers
        range_stop = sheet.nrows
        return reader, range_start, range_stop, sheet

    def validate_contents(self):
        ''' Validates the CSV/XLS contents based on customized rules '''

        product_model = self.env['product.product']
        currency_mapping_model = self.env['product_import_vendor_cart.currency_mapping']
        uom_mapping_model = self.env['product_import_vendor_cart.uom_mapping']
        new_product_line_model = self.env['product_import_vendor_cart.import_product_line']
        file_format = self.vendor_settings_id.file_format
        encoding = self.vendor_settings_id.encoding

        # Find the header row
        if file_format == 'csv':
            delimiter = str(self.vendor_settings_id.delimiter)
            reader, range_start, range_stop, csv_rows = self.get_csv_reader(delimiter)
            sheet = False
            header_row = next(reader, None)
        else:
            reader, range_start, range_stop, sheet = self.get_xls_reader()
            csv_rows = False
            header_index = self.vendor_settings_id.row_with_headers - 1
            header_row = sheet.row(header_index)

        # Check that the number of columns in the header is the same for both the file and the mapping
        if file_format == 'csv':
            if len(header_row) != len(self.vendor_settings_id.field_mapping_ids):
                self.add_issue(self.vendor_settings_id.row_with_headers, 'Header', u'Number of columns does not match. Expecting {} columns but the CSV has {}.'.format(len(self.vendor_settings_id.field_mapping_ids), len(header_row)))
        else:
            if sheet.ncols != len(self.vendor_settings_id.field_mapping_ids):
                self.add_issue(self.vendor_settings_id.row_with_headers, 'Header', u'Number of columns does not match. Expecting {} columns but the XLS has {}.'.format(len(self.vendor_settings_id.field_mapping_ids), sheet.ncols))

        # Check that all the columns defined in mappings exist in the file
        mapping_headers = []
        identifying_field = False

        for mapping in self.vendor_settings_id.field_mapping_ids:
            mapping_headers.append(mapping.column_name)
            if file_format == 'csv':
                if mapping.column_name not in [header_string.decode(encoding) for header_string in header_row]:
                    self.add_issue(self.vendor_settings_id.row_with_headers, 'Header', u'Column "{}" is missing from CSV.'.format(mapping.column_name))
            else:
                if mapping.column_name not in [x.value for x in header_row]:
                    self.add_issue(self.vendor_settings_id.row_with_headers, 'Header', u'Column "{}" is missing from XLS.'.format(mapping.column_name))

            # Check that the field that has been marked as being the identifying field is mapped to something
            for product_field_id in mapping.product_field_ids:
                if product_field_id.id == self.vendor_settings_id.identifying_field_id.id:
                    identifying_field = True

        if not identifying_field:
            self.add_issue(self.vendor_settings_id.row_with_headers, 'Identifying column', u'"{}" is defined as an identifying field but it has not been mapped.'.format(self.vendor_settings_id.identifying_field_id.field_description))

        # If all the columns are not present, do not continue with the rest of the validation
        if self.issue_ids:
            return

        # Check that the columns are in the same order in the file's header and in the mapping
        if file_format == 'csv':
            column_range = len(header_row)
        else:
            column_range = sheet.ncols

        for col_index in range(column_range):
            if file_format == 'csv':
                cell_header = header_row[col_index].decode(encoding)
            else:
                cell_header = sheet.cell(header_index, col_index).value

            mapping_header = mapping_headers[col_index]
            if cell_header != mapping_header:
                self.add_issue(self.vendor_settings_id.row_with_headers, 'Header', u'Column "{}" and mapped field "{}" are not in the same order. Please check the column mapping configuration.'.format(cell_header, mapping_header))

        # If there were errors in validating the structure, don't even start validating the rows
        if self.issue_ids:
            self.message_validation_error = 'Found the following issues with the {} file. The Vendor Template does not match the Shopping Cart file data.'.format(file_format)
            return

        ''' Iterate content rows from the header+1 row onwards '''
        for row_number in range(range_start, range_stop):

            # Stop iteration at the first encountered empty row (=empty first cell)
            if self.get_cell_value(file_format, row_number, 0, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False) == '':
                break

            for mapping in self.vendor_settings_id.field_mapping_ids:
                if mapping.product_field_ids:

                    for product_field_id in mapping.product_field_ids:
                        if product_field_id.id == self.vendor_settings_id.identifying_field_id.id:
                            identifying_field_value = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            existing_products = product_model.search([(self.vendor_settings_id.identifying_field_id.name, '=', identifying_field_value)])
                            # Check if the product matching the identifying field already exists. If yes, indicate that it will be updated
                            if not existing_products:
                                new_product_line_model.create({
                                    'name': identifying_field_value,
                                    'wizard_id': self.id,
                                })
                            else:
                                for ep in existing_products:
                                    self.existing_product_ids = [(4, ep.id)]
                if mapping.supplierinfo_field_ids:
                    for supplierinfo_field_id in mapping.supplierinfo_field_ids:
                        # Check that currencies and UOMs are mapped
                        if supplierinfo_field_id.ttype == 'many2one' and supplierinfo_field_id.relation == 'res.currency':
                            search_term = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            matching_currency_mappings = currency_mapping_model.search(args=[('value_in_file', '=', search_term)], limit=1)
                            if not matching_currency_mappings:
                                self.add_issue(row_number, 'Invalid Currency', u'Currency "{}" has not been mapped to any Odoo currency.'.format(search_term))
                        elif supplierinfo_field_id.ttype == 'many2one' and supplierinfo_field_id.relation == 'product.uom':
                            search_term = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            matching_uom_mappings = uom_mapping_model.search(args=[('value_in_file', '=', search_term)], limit=1)
                            if not matching_uom_mappings:
                                self.add_issue(row_number, 'Invalid UoM', u'UoM "{}" has not been mapped to any Odoo Unit of Measure.'.format(search_term))

        if self.issue_ids:
            self.message_validation_error = 'Found the following issues with the {} file. The shopping cart rows contain unmapped currencies or units of measure.'.format(file_format)
        else:
            self.message_validation_ok = u'Validating file columns was successful, you can proceed with the import. The import will create / update the following products:'

    def get_cell_value(self, file_format, row, col, excel_data, csv_data, strip_nonnumeric=False):
        ''' Get the contents of a specific cell. Strip nonnumerics for monetary fields with currencies in them, e.g Farnell's "EUR 34.72" '''
        if file_format == 'csv':
            stripped = csv_data[row][col].strip()
            if strip_nonnumeric:
                stripped = ''.join(c for c in stripped if c in set('1234567890.,'))
            return stripped
        else:
            return excel_data.cell(row, col).value

    def import_products(self):
        '''Import product data from CSV/XLS'''

        product_model = self.env['product.product']
        supplierinfo_model = self.env['product.supplierinfo']
        currency_mapping_model = self.env['product_import_vendor_cart.currency_mapping']
        uom_mapping_model = self.env['product_import_vendor_cart.uom_mapping']

        file_format = self.vendor_settings_id.file_format

        # Read in the CSV or XLS file contents
        csv_rows = False
        sheet = False
        if file_format == 'csv':
            delimiter = str(self.vendor_settings_id.delimiter)
            reader, range_start, range_stop, csv_rows = self.get_csv_reader(delimiter)
        else:
            reader, range_start, range_stop, sheet = self.get_xls_reader()

        ''' Iterate content rows from the header+1 row onwards '''
        for row_number in range(range_start, range_stop):

            # Stop iteration at the first encountered empty row (=empty first cell)
            if self.get_cell_value(file_format, row_number, 0, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False) == '':
                break

            # Placeholder dictionaries for storing product and supplierinfo row values
            product_vals = {}
            supplierinfo_vals = {}

            # Value of the field specified in vendor settings, e.g. manufacturer code
            # If found, is used to update existing product
            identifying_field_value = False

            # Go through all mapping rows that have product or supplierinfo counterpart fields defined
            for mapping in self.vendor_settings_id.field_mapping_ids:

                if mapping.product_field_ids:
                    for product_field_id in mapping.product_field_ids:
                        if product_field_id.ttype == 'many2one':
                            # Rudimentary handling for m2o fields pointing to res.partner (other types are not currently allowed):

                            # Search case-insensitively for records that are named with the cell contents, e.g. "NEUTRIK"
                            target_model = self.env[product_field_id.relation]
                            search_term = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            # If there are duplicates found, ignore them and just use the first result
                            matching_target = target_model.search(args=[('name', '=ilike', search_term)], limit=1)

                            if matching_target:
                                # Link the product to the m2o target model
                                product_vals[product_field_id.name] = matching_target[0].id
                            else:
                                # Create a new object if there was no match, and link the product to it
                                target_res = target_model.create({
                                    'name': search_term
                                })
                                product_vals[product_field_id.name] = target_res.id
                        else:
                            # Strip nonnumeric characters if the target field is numeric, in case the field contains e.g. currency with the value, e.g. "34.72 EUR" 
                            if product_field_id.ttype in ['integer', 'float']:
                                strip_nonnumeric = True
                            else:
                                strip_nonnumeric = False

                            product_vals[product_field_id.name] = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=strip_nonnumeric)

                        # Also store the value of the identifying product field (e.g. manufacturer code), so that
                        # we can search later if such product already exists.
                        if product_field_id.id == self.vendor_settings_id.identifying_field_id.id:
                            identifying_field_value = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)

                if mapping.supplierinfo_field_ids:
                    for supplierinfo_field_id in mapping.supplierinfo_field_ids:
                        if supplierinfo_field_id.ttype == 'many2one' and supplierinfo_field_id.relation == 'res.currency':
                            search_term = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            matching_currency_mappings = currency_mapping_model.search(args=[('value_in_file', '=', search_term)], limit=1)

                            if matching_currency_mappings:
                                supplierinfo_vals[supplierinfo_field_id.name] = matching_currency_mappings[0].currency_id.id
                            else:
                                raise exceptions.except_orm('Error', 'Currency "{}" has not been mapped to any Odoo currency.'.format(search_term))
                        elif supplierinfo_field_id.ttype == 'many2one' and supplierinfo_field_id.relation == 'product.uom':
                            search_term = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=False)
                            matching_uom_mappings = uom_mapping_model.search(args=[('value_in_file', '=', search_term)], limit=1)

                            if matching_uom_mappings:
                                supplierinfo_vals[supplierinfo_field_id.name] = matching_uom_mappings[0].uom_id.id
                            else:
                                raise exceptions.except_orm('Error', 'UoM "{}" has not been mapped to any Odoo Unit of Measure.'.format(search_term))
                        else:
                            if supplierinfo_field_id.ttype in ['integer', 'float']:
                                strip_nonnumeric = True
                            else:
                                strip_nonnumeric = False
                            supplierinfo_vals[supplierinfo_field_id.name] = self.get_cell_value(file_format, row_number, mapping.column_number - 1, excel_data=sheet, csv_data=csv_rows, strip_nonnumeric=strip_nonnumeric)

            # Check if we should create a new product or update an existing one
            if identifying_field_value and identifying_field_value.strip() != '':
                existing_products = product_model.search([(self.vendor_settings_id.identifying_field_id.name, '=', identifying_field_value)])
            else:
                existing_products = False

            if not existing_products:
                # Create a new product and a new supplierinfo row for it
                res = product_model.create(product_vals)
                supplierinfo_vals['product_tmpl_id'] = res.product_tmpl_id.id
                supplierinfo_vals['name'] = self.vendor_settings_id.partner_id.id
                supplierinfo_model.create(supplierinfo_vals)
            else:

                # Update the products
                existing_products.write(product_vals)

                # Check all products individually if their supplierinfo should be updated as well
                for existing_product in existing_products:

                    # Check for existing supplierinfo row for the product and vendor
                    existing_supplierinfo = supplierinfo_model.search(args=[('product_tmpl_id', '=', existing_product.product_tmpl_id.id),
                                                                            ('name', '=', self.vendor_settings_id.partner_id.id)])

                    if existing_supplierinfo:
                        existing_supplierinfo.write(supplierinfo_vals)
                    else:
                        supplierinfo_vals['product_tmpl_id'] = existing_product.product_tmpl_id.id
                        supplierinfo_vals['name'] = self.vendor_settings_id.partner_id.id
                        supplierinfo_model.create(supplierinfo_vals)

    product_file = fields.Binary('Shopping Cart File')
    vendor_settings_id = fields.Many2one('product_import_vendor_cart.vendor_settings', 'Vendor Template')
    state = fields.Selection([('file_selection', 'File Selection'),
                              ('validation', 'Validation'),
                              ('done', 'Done')], default='file_selection')

    message_validation_ok = fields.Char('Validation OK Message')
    message_validation_error = fields.Char('Validation Error Message')
    message_done = fields.Char('Done Message')
    issue_ids = fields.One2many('product_import_vendor_cart.import_wizard_issue', 'wizard_id', 'Issues:')
    existing_product_ids = fields.Many2many('product.product', string='Existing Products')
    new_product_line_ids = fields.One2many('product_import_vendor_cart.import_product_line', 'wizard_id', string="New Products")
