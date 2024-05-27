###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models
from datetime import datetime

class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["helpdesk.ticket", "hr.timesheet.time_control.mixin"]

    @api.model
    def _relation_with_timesheet_line(self):
        return "ticket_id"

    allow_timesheet = fields.Boolean(
        string="Allow Timesheet",
        related="team_id.allow_timesheet",
    )
    planned_hours = fields.Float(tracking=True)

    @api.onchange('sla_id')
    def get_planned_hours(self):
        if self.sla_id:
            self.planned_hours = self.sla_id.time
    progress = fields.Float(
        compute="_compute_progress_hours",
        group_operator="avg",
        store=True,
    )
    remaining_hours = fields.Float(
        compute="_compute_progress_hours",
        readonly=True,
        store=True,
    )
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="ticket_id",
        string="Timesheet",
    )
    total_hours = fields.Float(
        compute="_compute_total_hours", readonly=True, store=True
    )
    last_timesheet_activity = fields.Date(
        compute="_compute_last_timesheet_activity",
        readonly=True,
        store=True,
    )

    @api.depends("timesheet_ids.unit_amount")
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.timesheet_ids.mapped("unit_amount"))

    @api.constrains("project_id")
    def _constrains_project_timesheets(self):
        for record in self:
            record.timesheet_ids.update({"project_id": record.project_id.id})

    @api.onchange("team_id")
    def _onchange_team_id(self):
        for record in self.filtered(lambda a: a.team_id and a.team_id.allow_timesheet):
            record.project_id = record.team_id.default_project_id

    @api.depends("planned_hours", "total_hours")
    def _compute_progress_hours(self):
        for ticket in self:
            ticket.progress = 0.0
            if ticket.planned_hours > 0.0:
                if ticket.total_hours > ticket.planned_hours:
                    ticket.progress = 100
                else:
                    ticket.progress = round(
                        100.0 * ticket.total_hours / ticket.planned_hours, 2
                    )
            ticket.remaining_hours = ticket.planned_hours - ticket.total_hours

    @api.depends("timesheet_ids.date")
    def _compute_last_timesheet_activity(self):
        for record in self:
            record.last_timesheet_activity = (
                record.timesheet_ids
                and record.timesheet_ids.sorted(key="date", reverse=True)[0].date
            ) or False

    @api.depends(
        "team_id.allow_timesheet",
        "project_id.allow_timesheets",
        "timesheet_ids.employee_id",
        "timesheet_ids.unit_amount",
    )
    def _compute_show_time_control(self):
        result = super()._compute_show_time_control()
        for ticket in self:
            if not (
                ticket.project_id.allow_timesheets and ticket.team_id.allow_timesheet
            ):
                ticket.show_time_control = False
        return result

    def button_start_work(self):
        result = super().button_start_work()
        result["context"].update(
            {
                "default_project_id": self.project_id.id,
                "default_task_id": self.task_id.id,
            }
        )
        return result

    # timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', string='Timesheet Entries')
    total_work_duration = fields.Float(string='Total Work Duration (Hours)', compute='_compute_total_work_duration')

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_work_duration(self):
        for ticket in self:
            ticket.total_work_duration = sum(timesheet.unit_amount for timesheet in ticket.timesheet_ids)

    def action_start_work(self):
        self.ensure_one()
        self.timesheet_ids.create({
            'ticket_id': self.id,
            'unit_amount': 0,
            'name': 'Work Started {}'.format(self.name),
            'user_id': self.env.user.id,
            'date': fields.datetime.today(),
            'project_id': self.project_id.id,
            'task_id': self.id,
        })

    def action_end_work(self):
        self.ensure_one()
        active_timesheets = self.timesheet_ids.filtered(lambda ts: not ts.unit_amount)
        if active_timesheets:
            active_timesheets[0].button_end_work()


    def action_set_closed(self):
        self.write({'state': 'closed','timer_end':datetime.now()})

    def action_set_in_progress(self):
        self.action_start_work()
        self.write({'state': 'in_progress', 'timer_start': datetime.now()})

    def action_resolve_ticket(self):
        self.action_end_work()
        self.write({'state': 'resolved','timer_end':datetime.now()})