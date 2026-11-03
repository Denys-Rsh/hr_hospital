from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrHospitalMedicInfo(models.AbstractModel):
    _name = 'hr.hospital.medic.info'
    _description = 'Hospital Medic Info'

    blood_type = fields.Selection(
        selection=[
            ('o_positive', 'O(I)+'),
            ('o_negative', 'O(I)-'),
            ('a_positive', 'A(II)+'),
            ('a_negative', 'A(II)-'),
            ('b_positive', 'B(III)+'),
            ('b_negative', 'B(III)-'),
            ('ab_positive', 'AB(IV)+'),
            ('ab_negative', 'AB(IV)-'),
        ],
        required=True,
        string='Blood Type',
    )
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        required=True,
        string='Gender',
    )
    birth_date = fields.Date(string='Birth Date', required=True)
    age = fields.Integer(string='Age', compute='_compute_age')

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            record.age = relativedelta(fields.Date.today(), record.birth_date).years if record.birth_date else 0
