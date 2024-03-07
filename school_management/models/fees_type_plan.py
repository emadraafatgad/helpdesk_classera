from odoo import fields, models


class SchoolFeesLines(models.Model):
    _name = 'school.fees.structure.plan.line'

    installment_id = fields.Many2one('school.installment')
    date = fields.Date()
    structure_id = fields.Many2one('school.fees.structure',)
    branch_id = fields.Many2one('res.branch', )
    level_id = fields.Many2one('school.level',)
    academic_year_id = fields.Many2one('academic.year', )

    fees_item_id = fields.Many2one('product.product', domain="[('is_fees','=',True)]")
    category_id = fields.Many2one(related='fees_item_id.categ_id')


class SchoolFeesType(models.Model):
    _name = 'school.fees.structure.plan'
    _inherit = ['mail.thread']

    is_default_plan = fields.Boolean()
    plan_id = fields.Many2one('school.fees.plan', required=True)
    structure_id = fields.Many2one('school.fees.structure', required=True)
    branch_id = fields.Many2one('res.branch', required=True)
    level_id = fields.Many2one('school.level', required=True)
    academic_year_id = fields.Many2one('academic.year', required=True)
    fees_items = fields.Many2many('product.product', domain="[('is_fees','=',True)]")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    amount = fields.Float()
