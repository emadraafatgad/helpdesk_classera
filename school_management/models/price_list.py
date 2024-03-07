from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.website.models import ir_http


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    level_ids = fields.Many2many('school.level',tracking=True)
