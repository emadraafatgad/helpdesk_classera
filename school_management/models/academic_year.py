from odoo import fields, models


class AcademicYear(models.Model):
    _name = 'academic.year'
    _inherit = ['mail.thread']
    _description = "Academic Year"
    _order = "name, company_id"

    name = fields.Char(required=True)
    classera_id = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    semester_numbers = fields.Integer()
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch')

