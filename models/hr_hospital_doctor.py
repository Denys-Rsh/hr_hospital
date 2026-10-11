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
        compute='_compute_doctor_id',
        store=True,
        readonly=False,
    )
    category_id = fields.Many2one(string='Категорія', comodel_name='hr.hospital.doctor.category')
    history_ids = fields.One2many(comodel_name='hr.hospital.doctor.history', inverse_name='doctor_id')
    user_id = fields.Many2one(comodel_name='res.users')
    is_intern = fields.Boolean(
        string='Інтерн',
        compute='_compute_is_intern',
        store=True,
    )

    @api.depends('category_id.name')
    def _compute_is_intern(self):
        """Розглядав три варіанти:
          1. Позначати лікаря як інтерна вручну. Відмовився, бо це не відповідає умові завдання: `is_intern` має бути
             обчислюваним полем.
          2. Перевіряти ознаку (прапорець) у категорії, яка вказує, що категорія відповідає інтерну.
          3. Порівнювати назву категорії з константою.

          Обрав варіант 3. Хоча варіант 2 зрозуміліший і не чутливий до перейменування категорії, варіант 3 має свої
          переваги: він відповідає умові завдання, простіший у реалізації та не потребує додаткового поля в базі даних.
          Обидва варіанти вразливі до видалення категорії, якщо не передбачено засобів захисту.
        """
        for record in self:
            record.is_intern = record.category_id.name == 'Intern'

    @api.depends('is_intern')
    def _compute_doctor_id(self):
        for record in self:
            if not record.is_intern:
                record.doctor_id = False

    @api.constrains('doctor_id')
    def _check_is_intern(self):
        if any(record.doctor_id.is_intern for record in self):
            raise ValidationError('Не можна зберегти запис, якщо обраний ментор є інтерном')
