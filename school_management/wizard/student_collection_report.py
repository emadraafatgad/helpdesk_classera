from odoo import fields, models, api


class StudentAnalysisCollection(models.TransientModel):
    _name = 'student.analysis.report.wizard'

    branch_id = fields.Many2one('res.branch', required=True)
    level_ids = fields.Many2many('school.level')
    academic_year_id = fields.Many2one('academic.year', required=True)
    installment_ids = fields.Many2many('school.installment', required=True)
    fees_group_ids = fields.Many2many('product.category')
    fees_ids = fields.Many2many('product.product', domain="[('is_fees','=',True)]")
    guardian_id = fields.Many2one('res.partner', domain="[('is_guardian','=',True)]")
    student_ids = fields.Many2many('res.partner', domain="[('is_student','=',True)]")
    summary_only = fields.Boolean()
    remaining_only = fields.Boolean()

    @api.onchange('branch_id')
    def get_branch_levels(self):
        if self.branch_id:
            levels = self.env['school.level'].search([('branch_id', '=', self.branch_id.id)])
            print(levels)
            if levels:
                self.level_ids = [(5, 0, 0)]
                self.level_ids = [(6, 0, levels.ids)]

    @api.onchange('guardian_id')
    def get_guardian_student(self):
        if self.guardian_id:
            self.student_ids = [(6, 0, self.env['res.partner'].search([('guardian_id', '=', self.guardian_id.id)]).ids)]

    def print_report_excel(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('school_management.school_student_analysis_xls_export').report_action(self, data=data)


class StudentAnalysisXlsx(models.AbstractModel):
    _name = 'report.school_management.student_analysis_xlsx'
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
