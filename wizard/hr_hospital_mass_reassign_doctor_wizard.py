from odoo import api, fields, models


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
    _name = 'hr.hospital.mass.reassign.doctor.wizard'
    _description = 'Hospital wizard'

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Пацієнти',
        default=lambda self: self._default_patient_ids(),
    )
    doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor', string='Новий Лікар', required=True)
    changing_date = fields.Date(default=fields.Date.today, string='Дата зміни')

    @api.model
    def _default_patient_ids(self):
        if self.env.context.get('active_model') == 'hr.hospital.patient':
            return [fields.Command.set(self.env.context.get('active_ids', []))]
        return False

    def action_reassign(self):
        self.ensure_one()
        self.patient_ids.write({'doctor_id': self.doctor_id.id})
        return {'type': 'ir.actions.act_window_close'}
