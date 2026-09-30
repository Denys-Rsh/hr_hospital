from odoo import fields, models


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Hospital disease'

    name = fields.Char(required=True)
