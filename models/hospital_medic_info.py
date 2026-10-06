from odoo import fields, models

class HospitalMedicInfo(models.AbstractModel):
    _name = 'hospital.medic_info'
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
        string='Група крові',
    )
    gender = fields.Selection(
        selection=[
            ('male', 'Чоловік'),
            ('female', 'Жінка'),
        ],
        required=True,
        string='Стать',
    )
    birth_date = fields.Date(string='Дата народження', required=True)
    age = fields.Integer(string='Вік', compute='_compute_age')

    def _compute_age(self):
        for record in self:
            record.age = fields.Date.today() - record.birth_date