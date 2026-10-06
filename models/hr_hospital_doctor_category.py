from odoo import fields, models


class HrHospitalDoctorCategory(models.Model):
    _name = 'hr.hospital.doctor.category'
    _description = 'Hospital doctor category'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=0)
    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='category_id',
    )

    _name_uniq = models.Constraint(
        'UNIQUE(name)',
        'Doctor category name must be unique.',
    )


