from datetime import datetime

from odoo import models, fields, api,_
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
        # ('closed', 'Closed')
    ], string='State', default='new', tracking=True)

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
    approved = fields.Boolean()
    def manager_approval_to_complete(self):
        print(self.env.user)
        self._compute_related_employee()
        print(self.sudo().manager_id)
        print(self.manager_id.user_id)
        if not self.to_approve_manager.user_id == self.env.user:
            raise ValidationError("You are not the Manager")
        self.approved = True
        # self.action_set_in_progress()

    def manager_reject_request(self):
        print(self.env.user)
        print(self.manager_id.user_id)
        if not self.manager_id.user_id == self.env.user:
            raise ValidationError("You are not the Manager")
        self.approved = True

    def action_request_approve(self):
        self.message_post(
            body=_("Please Approve (%s) .") % (self.name),
            partner_ids=self.manager_id.user_id.partner_id.id,
            subtype_id=self.env.ref('mail.mt_note').id,
            email_layout_xmlid='mail.mail_notification_light')
        stage = self.env['helpdesk.ticket.stage'].search([('state', '=', 'on_hold')], limit=1)
        if stage:
            self.write({'state': 'on_hold', 'stage_id': stage.id})
        else:
            self.write({'state': 'on_hold'})

    def action_set_closed(self):
        self.write({'state': 'closed'})

    def action_set_on_hold(self):
        pass

    def action_set_in_progress(self):
        stage = self.env['helpdesk.ticket.stage'].search([('state', '=', 'in_progress')], limit=1)
        if stage:
            self.write({'state': 'in_progress', 'stage_id': stage.id, 'timer_start': datetime.now()})
        else:
            self.write({'state': 'in_progress', 'timer_start': datetime.now()})

    def action_resolve_ticket(self):
        stage = self.env['helpdesk.ticket.stage'].search([('state', '=', 'resolved')], limit=1)
        if stage:
            self.write({'state': 'resolved', 'stage_id': stage.id, })
        else:
            self.write({'state': 'resolved' })

    def action_close_ticket(self):
        stage = self.env['helpdesk.ticket.stage'].search([('state', '=', 'closed')], limit=1)
        if stage:
            self.write({'state': 'closed', 'stage_id': stage.id,})
        else:
            self.write({'state': 'closed'})
