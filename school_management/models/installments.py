from odoo import fields, models


class SchoolInstallment(models.Model):
    _name = 'school.installment'
    _inherit = ['mail.thread']
    _description = "School Installments"
    _order = "name, company_id"

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    number = fields.Integer()


class SchoolPlan(models.Model):
    _name = 'school.plan'
    _inherit = ['mail.thread']
    _description = "School Plan"
    _order = "name, company_id"

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    number = fields.Integer()