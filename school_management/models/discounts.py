from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class DiscountTemplate(models.Model):
    _name = 'discount.template'
    _inherit = ['mail.thread']
    _description = "Discount Template"
    _order = "name, company_id"

    name = fields.Char(default="New")
    discount_category_id = fields.Many2one('product.product',domain="[('is_discount','=',True)]", required=True,tracking=True)
    academic_year_id = fields.Many2one('academic.year', required=True,tracking=True)
    level_ids = fields.Many2many('school.level', required=True,tracking=True)
    student_sequence_ids = fields.Many2many('student.sequence', required=True,tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True,tracking=True)


    installment_type = fields.Selection([('all','For All Installments'),('multi','Selected Installments'),('last','Last Installment')],default='all', required=True,tracking=True)
    installment_ids = fields.Many2many('school.installment', required=True,tracking=True)
    discount_type = fields.Selection([('amount','Amount'),('percentage','Percentage')],default='amount', required=True,tracking=True)
    discount = fields.Float(required=True,tracking=True)
    note = fields.Char(tracking=True)