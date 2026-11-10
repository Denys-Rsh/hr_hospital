from odoo import api, fields, models


class HrHospitalPatient(models.Model):
    """Patient of the hospital."""

    _name = 'hr.hospital.patient'
    _description = 'Hospital patient'
    _inherit = 'hr.hospital.medic.info'

    name = fields.Char(required=True)
    phone = fields.Char(string='Phone')
    policy_number = fields.Integer(string='Insurance Policy Number')
    policy_note = fields.Char(
        string='Policy Note',
        help='Original policy value that could not be converted to a number.',
    )
    doctor_id = fields.Many2one(string='Personal Doctor', comodel_name='hr.hospital.doctor')
    history_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.history',
        inverse_name='patient_id',
        string='History',
    )
    visit_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='patient_id',
        string='Visits',
    )
    visit_count = fields.Integer(string='Visit Count', compute='_compute_visit_count')
    user_id = fields.Many2one(comodel_name='res.users', string='System User')

    @api.depends('visit_ids')
    def _compute_visit_count(self):
        """Count the visits of each patient with a single grouped query."""
        counts = {}
        if self.ids:
            groups = self.env['hr.hospital.visit']._read_group(
                domain=[('patient_id', 'in', self.ids)],
                groupby=['patient_id'],
                aggregates=['__count'],
            )
            counts = {patient.id: count for patient, count in groups}
        for record in self:
            record.visit_count = counts.get(record.id, 0)

    def action_view_visits(self):
        """Open the list of visits of this patient."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Visits: %s', self.display_name),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def action_create_visit(self):
        """Open a popup form of a new visit for this patient and the personal doctor."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('New Visit'),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.doctor_id.id,
                'default_name': self.env._('Visit: %s', self.name),
            },
        }
