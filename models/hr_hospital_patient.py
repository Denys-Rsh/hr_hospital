from odoo import api, fields, models


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Hospital patient'
    _inherit = 'hr.hospital.medic.info'

    name = fields.Char(required=True)
    phone = fields.Char(string='Phone')
    insurance_policy_number = fields.Char(string='Insurance Policy Number', size=20)
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
