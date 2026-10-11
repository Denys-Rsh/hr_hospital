from odoo import fields, models


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Hospital patient'
    _inherit = 'hr.hospital.medic.info'

    name = fields.Char(required=True)
    insurance_policy_number = fields.Char(string='Insurance Policy Number', size=20)
    doctor_id = fields.Many2one(string='Personal Doctor', comodel_name='hr.hospital.doctor')
    history_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.history',
        inverse_name='patient_id',
        string='History',
    )
