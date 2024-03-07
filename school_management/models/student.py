from odoo import fields, models,api


class StudentSequence(models.Model):
    _name = 'student.sequence'
    _inherit = ['mail.thread']

    name = fields.Char()
    number = fields.Integer()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    english_name = fields.Char(required=True,tracking=True)
    is_student = fields.Boolean()
    is_guardian = fields.Boolean()
    academic_year_id = fields.Many2one('academic.year',required=True,tracking=True)
    stage_id = fields.Many2one('school.stage',required=True,tracking=True)
    level_id = fields.Many2one('school.level',required=True,tracking=True)
    class_id = fields.Many2one('school.class',required=True,tracking=True)
    subject_id = fields.Many2one('school.subject')
    national_id_iqama = fields.Char(required=True,tracking=True)
    student_sequence_id = fields.Many2one('student.sequence')
    date_of_birth = fields.Date()
    birth_place = fields.Char()
    passport_number = fields.Char()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])

    guardian_id = fields.Many2one('res.partner', domain="[('is_guardian','=',True)]",required=True,tracking=True)
    father_national_id_iqama = fields.Char(related='guardian_id.national_id_iqama',readonly=False,string="Guardian National Id Iqama")
    father_nationality = fields.Many2one(related='guardian_id.country_id',readonly=False,string="Guardian Nationality")
    father_phone = fields.Char(related='guardian_id.phone',readonly=False,string="Guardian Phone")
    father_email = fields.Char(related='guardian_id.email',readonly=False,string="Guardian Email")

    fees_plan_id = fields.Many2one('school.fees.payment.plan',domain="[('levels_ids','in',level_id)]",required=True,tracking=True)
    discount_ids = fields.Many2many('discount.template', domain="[('level_ids','in',level_id)]", tracking=True)
    property_product_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist",
        company_dependent=False,
        domain=lambda self: [('company_id', 'in', (self.env.company.id, False)),('level_ids','in',[self.level_id.id])],
        help="This pricelist will be used, instead of the default one, for sales to the current partner")

    advanced_amount = fields.Float(compute='get_advanced_payment')

    @api.model
    def get_advanced_payment(self):
        for rec in self:
            advanced_payment = self.env['advance.payment'].search([('student_id','=',rec.id),('academic_year_id','=',rec.academic_year_id.id)])
            print(advanced_payment)
            rec.advanced_amount = sum(advanced_payment.mapped('total_amount'))

    def action_view_student_advanced(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("school_management.action_school_advance_payment_form")
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [
            ('student_id', 'in', all_child.ids)
        ]
        action['context'] = {'default_student_id': self.id, 'default_academic_year_id': self.academic_year_id.id}
        return action

    def action_view_student_payments(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments")
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [
            ('partner_id', 'in', all_child.ids)
        ]
        action['context'] = {'default_partner_id':self.id,'default_payment_type':'inbound','default_academic_year_id':self.academic_year_id.id}
        return action