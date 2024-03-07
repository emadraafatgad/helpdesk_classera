from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_ids = fields.Many2many('discount.template', domain="[('level_ids','in',level_id)]", tracking=True)

class AccountMove(models.Model):
    _inherit = 'account.move'

    academic_year_id = fields.Many2one('academic.year', compute="get_student_profile_date", store=True, tracking=True,
                                       readonly=False)
    stage_id = fields.Many2one('school.stage', compute="get_student_profile_date", store=True, tracking=True)
    level_id = fields.Many2one('school.level', compute="get_student_profile_date", store=True, tracking=True)
    class_id = fields.Many2one('school.class', compute="get_student_profile_date", store=True, tracking=True)
    national_id_iqama = fields.Char(compute="get_student_profile_date", tracking=True)
    student_sequence_id = fields.Many2one('student.sequence', compute="get_student_profile_date", tracking=True)
    guardian_id = fields.Many2one('res.partner', domain="[('is_guardian','=',True)]",
                                  compute="get_student_profile_date", tracking=True, store=True)
    fees_plan_id = fields.Many2one('school.fees.payment.plan', compute="get_student_fees_plan",readonly=False,
                                   domain="[('levels_ids','in',level_id)]", tracking=True)
    has_fees_plan = fields.Boolean(default=True, compute="get_student_fees_plan", tracking=True)
    installment_ids = fields.Many2many('school.installment')
    discount_ids = fields.Many2many('discount.template', domain="[('level_ids','in',level_id)]",compute="compute_fees_to_invoice_lines", tracking=True)

    # def compute_discount_percentage(self):
    #     if self.discount_ids:

    @api.depends('partner_id')
    def compute_fees_to_invoice_lines(self):
        for rec in self:
            if rec.partner_id:
                rec.discount_ids = [(6,0,rec.partner_id.discount_ids.ids)]
            else:
                rec.discount_ids = False

    @api.depends('partner_id')
    def get_student_fees_plan(self):
        for rec in self:
            print("compute fees plan",rec.partner_id)
            if rec.partner_id and rec.partner_id.fees_plan_id:
                rec.fees_plan_id = rec.partner_id.fees_plan_id.id
                rec.has_fees_plan = True
            else:
                rec.fees_plan_id = False
                rec.has_fees_plan = False

    @api.depends('partner_id')
    def get_student_profile_date(self):
        for rec in self:
            if rec.partner_id:
                rec.stage_id = rec.partner_id.stage_id.id
                rec.level_id = rec.partner_id.level_id.id
                rec.class_id = rec.partner_id.level_id.id
                rec.academic_year_id = rec.partner_id.academic_year_id.id
                rec.national_id_iqama = rec.partner_id.national_id_iqama
                rec.student_sequence_id = rec.student_sequence_id.id
                rec.guardian_id = rec.guardian_id.id
            else:
                rec.stage_id = False
                rec.level_id = False
                rec.class_id = False
                rec.academic_year_id = False
                rec.national_id_iqama = False
                rec.student_sequence_id = False
                rec.guardian_id = False

    # @api.onchange('fees_plan_id','partner_id')
    def onchange_invoice_fees_plan_id(self):
        print("iam in invoice fees plan")
        if self.fees_plan_id and self.state == 'draft':
            fees_plan_id = self.fees_plan_id
            old_invoices = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('id','!=',self.id),('move_type','in',['out_invoice','out_refund']),('academic_year_id','=',self.academic_year_id.id)])
            print('old_invoices')
            print(old_invoices)
            print(old_invoices.invoice_line_ids)
            #ADD REFUND INVOICE LINES
            old_lines = old_invoices.invoice_line_ids.filtered(lambda i :i.installment_id.id in self.installment_ids.ids)
            order_lines_data = []
            for line in fees_plan_id.plan_lines_ids.filtered(lambda i: i.installment_id.id in self.installment_ids.ids):
                plan_line_value = line._prepare_order_line_values(old_lines.filtered(
                    lambda i: i.installment_id.id == line.installment_id.id and line.product_id == i.product_id),self.discount_ids)
                if plan_line_value:
                    order_lines_data += [(fields.Command.create(plan_line_value))]
                    print('order_lines_data')
                    print(order_lines_data)
            self.invoice_line_ids = [fields.Command.clear()]
            print(order_lines_data)
            self.invoice_line_ids = order_lines_data


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    installment_id = fields.Many2one('school.installment')
