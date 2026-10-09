from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Hospital visit'

    name = fields.Char(required=True)
    status = fields.Selection(
        selection=[
            ('scheduled', 'Заплановано'),
            ('completed', 'Завершено'),
            ('cancelled', 'Скасовано'),
        ],
        string='Статус візиту'
    )
    scheduled_datetime = fields.Datetime(string='Заплановану дату та час візиту')
    visit_datetime = fields.Datetime(string='Дату та час, коли візит відбувся')
    doctor_id = fields.Many2one(string='Лікар', comodel_name='hr.hospital.doctor')
    patient_id = fields.Many2one(string='Пацієнт', comodel_name='hr.hospital.patient')
    summary = fields.Html(string='Епікриз')
    disease_id = fields.Many2one(comodel_name='hr.hospital.disease', string='Хвороба')
    active = fields.Boolean(default=True)

    @api.onchange('visit_datetime', 'scheduled_datetime', 'doctor_id', 'active')
    def _onchange_fields(self):
        if self.status == 'completed':
            return {
                'warning': {
                    'title': 'Візит',
                    'message': 'Заборонено змінювати час, дату або лікаря візиту, що вже відбувся.',
                },
            }
        return None

    @api.constrains('visit_datetime', 'scheduled_datetime', 'doctor_id', 'active')
    def _check_fields(self):
        for record in self:
            if record.status == 'completed':
                raise ValidationError('Заборонено змінювати час, дату або лікаря візиту, що вже відбувся.')

    @api.ondelete(at_uninstall=False)
    def _unlink_except_visited(self):
        if any(record.status == 'completed' for record in self):
            raise UserError(
                'Заборонено видаляти запис візиту, що вже відбувся.'
            )

