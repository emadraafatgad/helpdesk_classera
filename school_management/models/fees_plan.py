from odoo import fields, models, api


class SchoolFeesPlan(models.Model):
    _name = 'school.fees.plan'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    branch_id = fields.Many2one('res.branch', tracking=True)
    academic_year_id = fields.Many2one('academic.year', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    number = fields.Integer(required=True, tracking=True)


class SchoolFeesInstallmentPlan(models.Model):
    _name = 'school.fees.payment.plan'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    branch_id = fields.Many2one('res.branch', tracking=True)
    academic_year_id = fields.Many2one('academic.year', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    plan_id = fields.Many2one('school.fees.plan', required=True, tracking=True)
    levels_ids = fields.Many2many('school.level', required=True, tracking=True)
    plan_lines_ids = fields.One2many('school.fees.payment.plan.line', 'payment_plan_id')


class SchoolFeesInstallmentPlanLines(models.Model):
    _name = 'school.fees.payment.plan.line'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.product', required=True, tracking=True)
    installment_id = fields.Many2one('school.installment', required=True)
    branch_id = fields.Many2one('res.branch', tracking=True)
    levels_ids = fields.Many2many('school.level', required=True, tracking=True)
    academic_year_id = fields.Many2one('academic.year', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    payment_plan_id = fields.Many2one('school.fees.payment.plan', required=True, tracking=True)
    amount = fields.Float(required=True)
    subtotal = fields.Float(compute='calculate_subtotal_amount')
    total_amount = fields.Float(compute='calculate_subtotal_amount', string="If Tax applied")
    tax_ids = fields.Many2many('account.tax', domain="[('type_tax_use','=','sale')]")

    @api.onchange('product_id')
    def get_tax_ids(self):
        taxes = self.product_id.taxes_id
        # partner = self.payment_plan_id.student_id
        # if taxes and partner:
        #     fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(partner)
        #     if fiscal_position:
        #         taxes = fiscal_position.map_tax(taxes)
        self.tax_ids = [(6, 0, taxes.ids)]

    @api.depends('amount', 'product_id', 'tax_ids')
    def calculate_subtotal_amount(self):
        for rec in self:
            if rec.amount:
                rec.subtotal, rec.total_amount = rec.get_amount_from_tax(rec.product_id,
                                                                         rec.amount,
                                                                         rec.tax_ids)
            else:
                rec.subtotal = rec.total_amount = rec.amount

    def get_amount_from_tax(self, product_id, amount, tax_ids):
        price_subtotal = 0
        price_total = 0
        if amount:
            if tax_ids:
                taxes_res = tax_ids.compute_all(
                    amount,
                    quantity=1,
                    currency=self.env.company.currency_id,
                    product=product_id,
                    # partner=student_id,
                    is_refund=False,
                )
                price_subtotal = taxes_res['total_excluded']
                price_total = taxes_res['total_included']
            else:
                price_total = price_subtotal = amount
        return price_subtotal, price_total

    def compute_discount_amount(self, amount, discounts):
        discount_amount = 0
        for discount in discounts:
            print(discount,discount.installment_type,discount.discount_type)
            if discount.installment_type == 'all' and self.product_id.discount_allowed or (
                    discount.installment_type == 'multi' and self.installment_id.id in discount.installment_ids.ids) :
                if discount.discount_type == 'percentage':
                    discount_amount = discount.discount
                elif discount.discount_type == 'amount' and amount:
                    discount_amount = discount.discount / amount
            elif discount.installment_type == 'last':
                pass
        print(discount_amount)
        return discount_amount

    def _prepare_order_line_values(self, old_line, discounts=False):
        """ Give the values to create the corresponding order line.

        :return: `sale.order.line` create values
        :rtype: dict
        """
        print("iam in plan values")
        self.ensure_one()
        old_price = 0
        if old_line:
            old_price = sum(old_line.mapped('price_unit'))
        if old_price < self.amount:
            linevals = {
                # 'display_type': 'product',
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'quantity': 1,
                'discount': self.compute_discount_amount(self.amount - old_price, discounts),
                'price_unit': self.amount - old_price,
                'product_uom_id': self.product_id.uom_id.id,
                'installment_id': self.installment_id.id
            }
            print(linevals)
            return linevals
        else:
            print("else line")
            linevals = {
                # 'display_type': 'product',
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'quantity': 1,
                'price_unit': self.amount,
                'product_uom_id': self.product_id.uom_id.id,
                'installment_id': self.installment_id.id
            }
            return {}
