from odoo import models, fields,api
from datetime import datetime
from odoo.exceptions import ValidationError


class TicketSLA(models.Model):
    _name = 'ticket.sla'
    _description = 'Ticket SLA'

    name = fields.Char(string='SLA Name', required=True)
    time = fields.Float(string='SLA Time', required=True)



class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sla_id = fields.Many2one('ticket.sla', string='SLA')

    # contact_id = fields.Many2one('res.partner', string='Contact')
    related_employee_id = fields.Many2one('hr.employee', string=' Employee',
                                          compute='_compute_related_employee', store=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', compute='_compute_manager', store=True)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='State', default='new',tracking=True)

    @api.depends('partner_id')
    def _compute_related_employee(self):
        for ticket in self:
            if ticket.partner_id:
                employee = self.env['res.users'].search([('partner_id', '=', ticket.partner_id.id)], limit=1)
                ticket.related_employee_id = employee.employee_id
            else:
                ticket.related_employee_id = False

    @api.depends('related_employee_id')
    def _compute_manager(self):
        for ticket in self:
            print('ticket------------------')
            print(ticket.related_employee_id)
            if ticket.related_employee_id:
                ticket.manager_id = ticket.related_employee_id.parent_id
            else:
                ticket.manager_id = False

    timer_start = fields.Datetime(string='Timer Start')
    timer_end = fields.Datetime(string='Timer End')
    timer_duration = fields.Float(string='Timer Duration', compute='_compute_timer_duration')
    direct_manager_approval = fields.Boolean(related='category_id.direct_manager_approval')

    def manager_approval_to_complete(self):
        print(self.env.user)
        print(self.manager_id.user_id)
        if not self.manager_id.user_id == self.env.user:
            raise ValidationError("You are not the Manager")
        self.state = 'in_progress'

    def action_set_on_hold(self):
        self.write({'state': 'on_hold' })

    def action_set_closed(self):
        self.write({'state': 'closed'})

    def action_set_in_progress(self):
        self.write({'state': 'in_progress', 'timer_start': datetime.now()})

    def action_resolve_ticket(self):
        self.write({'state': 'resolved'})

    def action_clone_ticket(self):
        self.write({'state': 'resolved'})