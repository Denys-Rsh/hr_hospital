from odoo import api, fields, models
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
    mentor_name = fields.Char(related='doctor_id.name', string='ПІБ ментора')
    mentor_category_id = fields.Many2one(related='doctor_id.category_id', string='Категорія ментора')
    mentor_gender = fields.Selection(related='doctor_id.gender', string='Стать ментора')
    mentor_age = fields.Integer(related='doctor_id.age', string='Вік ментора')
    category_id = fields.Many2one(string='Категорія', comodel_name='hr.hospital.doctor.category')
    history_ids = fields.One2many(comodel_name='hr.hospital.doctor.history', inverse_name='doctor_id')
    user_id = fields.Many2one(comodel_name='res.users')
    is_intern = fields.Boolean(
        string='Інтерн',
        compute='_compute_is_intern',
        store=True,
    )
    intern_ids = fields.One2many(comodel_name='hr.hospital.doctor', inverse_name='doctor_id', string='Інтерни')
    patient_ids = fields.One2many(comodel_name="hr.hospital.patient", inverse_name="doctor_id")
    visit_ids = fields.One2many(comodel_name="hr.hospital.visit", inverse_name="doctor_id")

    @api.depends('category_id.name')
    def _compute_is_intern(self):
        """I considered three options:
        1. Marking the doctor as an intern manually. I rejected this because it violates the task requirements: `is_intern`
        must be a calculated field.
        2. Checking a flag on the category indicating that the category corresponds to an intern.
        3. Comparing the category name against a constant.

        I chose option 3. Although option 2 is clearer and resilient to category renaming, option 3 has its own
        advantages: it meets the task requirements, is simpler to implement, and does not require an additional
        database field. Both options are vulnerable to category deletion unless safeguards are in place.
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

    def action_quick_create_visit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Запис до лікаря: {self.name}',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'views': [(self.env.ref('hr_hospital.hr_hospital_visit_form').id, 'form')],
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
                'default_name': f'Візит до {self.name}',
                'default_scheduled_datetime': fields.Datetime.to_string(fields.Datetime.now()),
            },
        }
