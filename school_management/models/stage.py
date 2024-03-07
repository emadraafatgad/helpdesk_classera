from odoo import fields ,api,models,_


class SchoolStage(models.Model):
    _name = 'school.stage'
    _inherit = ['mail.thread']
    _description = "Academic Year"
    _order = "name, company_id"

    name = fields.Char(required=True,tracking=True)
    classera_id = fields.Char(tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,tracking=True,
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch')
