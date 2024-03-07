from odoo import fields ,api,models,_


class SchoolFeesStructure(models.Model):
    _name = 'school.fees.structure'
    _inherit = ['mail.thread']

    name = fields.Char( required=True)
    branch_id = fields.Many2one('res.branch', required=True)
    level_id = fields.Many2one('school.level', required=True)
    academic_year_id = fields.Many2one('academic.year', required=True)
    fees_items = fields.Many2many('product.product',domain="[('is_fees','=',True)]")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)