from odoo import fields, models


class SchoolStage(models.Model):
    _name = 'school.level'
    _inherit = ['mail.thread']
    _description = "School Levels"
    _order = "name, company_id"

    name = fields.Char(required=True)
    classera_id = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    stage_id = fields.Many2one('school.stage', required=True)
    sequence = fields.Integer()
    from_age = fields.Float()
    to_age = fields.Float()
    branch_id =  fields.Many2one('res.branch')
