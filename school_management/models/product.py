from odoo import fields, api, models


class PrductTemplate(models.Model):
    _inherit = 'product.template'

    is_fees = fields.Boolean()
    discount_allowed = fields.Boolean()
    advance_account_id = fields.Many2one('account.account')
    level_ids = fields.Many2many('school.level')
    is_discount = fields.Boolean()
    applied_fees_items_ids = fields.Many2many('product.product', domain="[('is_fees','=',True)]")
    allowed_users_ids = fields.Many2many('res.users')
    is_default_discount = fields.Boolean()

    @api.onchange('is_fees','is_discount')
    def get_sale_onchange_fees(self):
        self.sale_ok = self.is_fees
        if self.is_fees:
            self.detailed_type = 'service'
            self.purchase_ok = False
