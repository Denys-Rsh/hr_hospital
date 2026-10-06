from odoo import fields, models


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Hospital doctor'

    name = fields.Char(required=True)
    doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor')
    category_id = fields.Many2one(comodel_name='hr.hospital.doctor.category')
    history_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.history',
        inverse_name='doctor_id',
    )
