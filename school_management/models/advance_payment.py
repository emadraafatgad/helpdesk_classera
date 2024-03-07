from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

class AdvancedPayment(models.Model):
    _name = 'advance.payment'
    _inherit = ['mail.thread']
    _description = "Advance payment"
    _order = "name, company_id"

    name = fields.Char(default="New")
    date = fields.Date(required=True,tracking=True)
    student_id = fields.Many2one('res.partner', domain="[('is_student','=',True)]")
    academic_year_id = fields.Many2one('academic.year', required=True)
    level_id = fields.Many2one('school.level', required=True)
    stage_id = fields.Many2one('school.stage', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch')
    advance_line_ids = fields.One2many('advance.payment.line', 'advance_id')
    to_invoice = fields.Integer(default=-1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], readonly=True, default='draft')
    journal_id = fields.Many2one('account.journal', string="Payment Method", required=True, tracking=True,
                                 domain="[('type','in',['cash','bank'])]")
    invoice_id = fields.Many2one('account.move')
    total_amount = fields.Float(compute='calc_total_amount_lines',store=True)

    @api.depends('advance_line_ids')
    def calc_total_amount_lines(self):
        for rec in  self:
            rec.total_amount = sum(rec.advance_line_ids.mapped('total_amount'))

    @api.onchange('student_id')
    def student_info_from_profile(self):
        if self.student_id:
            self.academic_year_id = self.student_id.academic_year_id.id
            self.stage_id = self.student_id.stage_id.id
            self.level_id = self.student_id.level_id.id
            self.branch_id = self.student_id.branch_id.id

    def open_invoice_advanced_payment(self):
        return self.button_open_invoices()

    def button_open_invoices(self):
        ''' Redirect the user to the invoice(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Paid Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.invoice_id) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', [self.invoice_id.id])],
            })
        return action



    def create_invoice_for_advanced(self):
        customer_journal = self.env['account.journal'].search([('type','=','sale')],limit=1)
        if not customer_journal:
            raise ValidationError(_("Please Add Customer sale Journal"))
        if not self.advance_line_ids:
            raise ValidationError(_("Please Add Advanced Lines"))

        invoice = self.env['account.move'].create([
            {
                'move_type': 'out_invoice',
                'date': self.date,
                'invoice_date': self.date,
                'journal_id':customer_journal.id,
                'partner_id': self.student_id.id,
                'invoice_line_ids': [(0, 0, {
                'name': line.product_id.name,
                'price_unit': line.amount,
                'product_id': line.product_id.id,
                'quantity': 1.0,
                'account_id': line.product_id.advanced_account_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                'tax_ids': [(6,0,line.tax_ids.ids)],
            }) for line in self.advance_line_ids]
            },

        ])
        self.invoice_id = invoice.id
        invoice.action_post()
        if invoice:
            print("create register")
            payment = self.env['account.payment.register'].with_context(
                active_model='account.move', active_ids=[invoice.id]
            ).create({
                'payment_date': self.date,
                'amount': invoice.amount_total,
                'journal_id': self.journal_id.id,
                'currency_id': invoice.currency_id.id,
            })
            payment.action_create_payments()
        self.state='posted'

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning
        the the sequence for the record"""
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('advance.payment') or _('New')
        res = super(AdvancedPayment, self).create(vals)
        return res


class AdvancedPaymentLine(models.Model):
    _name = 'advance.payment.line'
    _inherit = ['mail.thread']
    _description = "Advance payment"

    product_id = fields.Many2one('product.product',
                                 domain="['|',('is_fees','=',True),('advance_account_id','!=',False)]", required=True,
                                 tracking=True)
    amount = fields.Float(required=True)
    tax_ids = fields.Many2many('account.tax', domain="[('type_tax_use','=','sale')]")
    subtotal = fields.Float(compute='calculate_subtotal_amount')
    total_amount = fields.Float(compute='calculate_subtotal_amount')
    advance_id = fields.Many2one('advance.payment')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    @api.onchange('product_id')
    def get_tax_ids(self):
        taxes = self.product_id.taxes_id
        partner = self.advance_id.student_id
        if taxes and partner:
            fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(partner)
            if fiscal_position:
                taxes = fiscal_position.map_tax(taxes)
        self.tax_ids = [(6, 0, taxes.ids)]

    @api.depends('amount', 'product_id', 'tax_ids')
    def calculate_subtotal_amount(self):
        for rec in self:
            if rec.amount:
                rec.subtotal, rec.total_amount = rec.get_amount_from_tax(rec.advance_id.student_id, rec.product_id,
                                                                         rec.amount,
                                                                         rec.tax_ids)
            else:
                rec.subtotal = rec.total_amount = rec.amount

    def get_amount_from_tax(self, student_id, product_id, amount, tax_ids):
        price_subtotal = 0
        price_total = 0
        if amount:
            if tax_ids:
                taxes_res = tax_ids.compute_all(
                    amount,
                    quantity=1,
                    currency=self.env.company.currency_id,
                    product=product_id,
                    partner=student_id,
                    is_refund=False,
                )
                price_subtotal = taxes_res['total_excluded']
                price_total = taxes_res['total_included']
            else:
                price_total = price_subtotal = amount
        return price_subtotal, price_total
