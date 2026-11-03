from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Hospital visit'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    status = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Visit Status',
        default='scheduled',
        tracking=True,
    )
    scheduled_datetime = fields.Datetime(string='Scheduled Date and Time')
    visit_datetime = fields.Datetime(string='Actual Visit Date and Time')
    doctor_id = fields.Many2one(string='Doctor', comodel_name='hr.hospital.doctor', tracking=True)
    patient_id = fields.Many2one(string='Patient', comodel_name='hr.hospital.patient')
    summary = fields.Html(string='Summary')
    disease_id = fields.Many2one(comodel_name='hr.hospital.disease', string='Disease')
    active = fields.Boolean(default=True)
    same_disease_visit_count = fields.Integer(
        string='Visits with the Same Disease',
        compute='_compute_same_disease_visit_count',
    )

    @api.depends('disease_id')
    def _compute_same_disease_visit_count(self):
        disease_ids = self.disease_id.ids
        counts = {}
        if disease_ids:
            groups = self._read_group(
                domain=[('disease_id', 'in', disease_ids)],
                groupby=['disease_id'],
                aggregates=['__count'],
            )
            counts = {disease.id: count for disease, count in groups}
        for record in self:
            record.same_disease_visit_count = counts.get(record.disease_id.id, 0)

    def action_view_same_disease_visits(self):
        self.ensure_one()
        if not self.disease_id:
            raise UserError(self.env._('No disease is set for this visit.'))
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Visits: %s', self.disease_id.display_name),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': [('disease_id', '=', self.disease_id.id)],
            'context': {'default_disease_id': self.disease_id.id},
        }

    def _get_overdue_visits_domain(self):
        return [
            ('status', '=', 'scheduled'),
            ('scheduled_datetime', '<', fields.Datetime.now()),
        ]

    def action_cancel_overdue_visits(self):
        overdue = self.filtered_domain(self._get_overdue_visits_domain())
        overdue.write({'status': 'cancelled'})
        return overdue

    @api.model
    def _cron_cancel_overdue_visits(self):
        return self.search(self._get_overdue_visits_domain()).action_cancel_overdue_visits()

    @api.onchange('visit_datetime', 'scheduled_datetime', 'doctor_id', 'active')
    def _onchange_fields(self):
        if self.status == 'completed':
            return {
                'warning': {
                    'title': self.env._('Visit'),
                    'message': self.env._('It is not allowed to change the time, date or doctor of a completed visit.'),
                },
            }
        return None

    @api.constrains('visit_datetime', 'scheduled_datetime', 'doctor_id', 'active')
    def _check_fields(self):
        for record in self:
            if record.status == 'completed':
                raise ValidationError(
                    self.env._('It is not allowed to change the time, date or doctor of a completed visit.')
                )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_visited(self):
        if any(record.status == 'completed' for record in self):
            raise UserError(self.env._('It is not allowed to delete a completed visit.'))
