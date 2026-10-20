from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


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
        string='Статус візиту',
        default='scheduled',
    )
    scheduled_datetime = fields.Datetime(string='Заплановану дату та час візиту')
    visit_datetime = fields.Datetime(string='Дату та час, коли візит відбувся')
    doctor_id = fields.Many2one(string='Лікар', comodel_name='hr.hospital.doctor')
    patient_id = fields.Many2one(string='Пацієнт', comodel_name='hr.hospital.patient')
    summary = fields.Html(string='Епікриз')
    disease_id = fields.Many2one(comodel_name='hr.hospital.disease', string='Хвороба')
    active = fields.Boolean(default=True)
    same_disease_visit_count = fields.Integer(
        string='Візити з такою ж хворобою',
        compute='_compute_same_disease_visit_count',
    )

    @api.depends('disease_id')
    def _compute_same_disease_visit_count(self):
        disease_ids = self.disease_id.ids
        counts = {}
        if disease_ids:
            groups = self._read_group(
                domain=[('disease_id', 'in', disease_ids)],
                groupby=['disease_id'],
                aggregates=['__count'],
            )
            counts = {disease.id: count for disease, count in groups}
        for record in self:
            record.same_disease_visit_count = counts.get(record.disease_id.id, 0)

    def action_view_same_disease_visits(self):
        self.ensure_one()
        if not self.disease_id:
            raise UserError('Для цього візиту не вказано хворобу.')
        return {
            'type': 'ir.actions.act_window',
            'name': f'Візити: {self.disease_id.display_name}',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': [('disease_id', '=', self.disease_id.id)],
            'context': {'default_disease_id': self.disease_id.id},
        }

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
            raise UserError('Заборонено видаляти запис візиту, що вже відбувся.')
