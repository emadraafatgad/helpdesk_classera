from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'

    is_fees = fields.Boolean()
    discount_allowed = fields.Boolean()
    advanced_account_id = fields.Many2one('account.account')