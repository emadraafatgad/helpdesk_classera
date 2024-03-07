from odoo import fields, models,api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    academic_year_id = fields.Many2one('academic.year', compute="get_student_profile_date", store=True, tracking=True,
                                       readonly=False)
    stage_id = fields.Many2one('school.stage', compute="get_student_profile_date", store=True, tracking=True)
    level_id = fields.Many2one('school.level', compute="get_student_profile_date", store=True, tracking=True)
    class_id = fields.Many2one('school.class', compute="get_student_profile_date", store=True, tracking=True)
    national_id_iqama = fields.Char(compute="get_student_profile_date", tracking=True)
    guardian_id = fields.Many2one('res.partner', domain="[('is_guardian','=',True)]",
                                  compute="get_student_profile_date", tracking=True, store=True)

    @api.depends('partner_id')
    def get_student_profile_date(self):
        for rec in self:
            if rec.partner_id:
                rec.stage_id = rec.partner_id.stage_id.id
                rec.level_id = rec.partner_id.level_id.id
                rec.class_id = rec.partner_id.level_id.id
                rec.academic_year_id = rec.partner_id.academic_year_id.id
                rec.national_id_iqama = rec.partner_id.national_id_iqama
                rec.guardian_id = rec.guardian_id.id
            else:
                rec.stage_id = False
                rec.level_id = False
                rec.class_id = False
                rec.academic_year_id = False
                rec.national_id_iqama = False
                rec.guardian_id = False
