from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Hospital doctor'
    _inherit = 'hr.hospital.medic.info'

    name = fields.Char(required=True)
    doctor_id = fields.Many2one(
        string='Ментор',
        comodel_name='hr.hospital.doctor',
        domain=[('is_intern', '=', False)],
    )
    category_id = fields.Many2one(string='Категорія', comodel_name='hr.hospital.doctor.category')
    history_ids = fields.One2many(comodel_name='hr.hospital.doctor.history', inverse_name='doctor_id')
    user_id = fields.Many2one(comodel_name='res.users')
    is_intern = fields.Boolean(default=False)

    @api.constrains('doctor_id')
    def _check_is_intern(self):
        if any(record.doctor_id.is_intern for record in self):
            raise ValidationError('Не можна зберегти запис, якщо обраний ментор є інтерном')
