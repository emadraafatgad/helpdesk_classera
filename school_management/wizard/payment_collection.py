from odoo import fields, models
import json

class CustomerPaymentCollection(models.TransientModel):
    _name = 'customer.payment.report.wizard'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    def print_report_excel(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('school_management.school_payment_collection_xls_export').report_action(self, data=data)

    def print_report_pdf(self):
        payments = self.env['account.payment'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to)])
        print(payments)
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'payments': json.dumps(payments),
        }
        return self.env.ref('school_management.school_payment_collection_pdf_export').report_action(self, data=data)


class CustomerPaymentXlsx(models.AbstractModel):
    _name = 'report.school_management.customer_payment_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # Your logic to generate the Excel report based on the provided data
        # Fetch and process data using 'data' dictionary (start_date, end_date)
        # Add data to Excel file using workbook and worksheet objects
        # Example:
        worksheet = workbook.add_worksheet('Customer Payments')
        title_style = workbook.add_format(
            {'valign': 'vcenter', 'align': 'center', 'border': 2, 'size': 12, 'font_color': 'red',
             'bg_color': '#fff2cc', 'bold': True})
        title_style.set_border(2)
        title_style.set_top()
        title_style.set_bottom()
        cell_style = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'text_wrap': True})
        # Add headers, data, formatting, etc. to the worksheet
        # Save the workbook (mandatory)
        payments = self.env['account.payment'].search(
            [('date', '>=', data['date_from']), ('date', '<=', data['date_to'])])
        print(payments)
        row = 2

        worksheet.write(1, 3, "Payment Collect", title_style)
        worksheet.write(row, 0, "Student", title_style)
        worksheet.write(row, 0, "Customer", title_style)
        worksheet.write(row, 1, "Date", title_style)
        worksheet.write(row, 2, "Method", title_style)
        worksheet.write(row, 3, "Amount", title_style)

        for payment in payments:
            row += 1
            worksheet.write(row, 0, payment.partner_id.name, cell_style)
            worksheet.write(row, 1, payment.date, cell_style)
            worksheet.write(row, 2, payment.journal_id.name, cell_style)
            worksheet.write(row, 3, payment.amount, cell_style)
