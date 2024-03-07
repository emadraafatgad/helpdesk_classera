from odoo import fields ,api,models,_


class SchoolStage(models.Model):
    _name = 'school.class'
    _inherit = ['mail.thread']
    _description = "School Classes"
    _order = "name, company_id"

    name = fields.Char(required=True)
    classera_id = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    level_id = fields.Many2one('school.level',required=True)