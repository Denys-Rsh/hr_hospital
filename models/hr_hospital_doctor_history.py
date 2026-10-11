from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDoctorHistory(models.Model):
    _name = 'hr.hospital.doctor.history'
    _description = 'Hospital doctor history'

    # name = fields.Char(required=True)
    patient_id = fields.Many2one(comodel_name='hr.hospital.patient', required=True)  # — Many2one, required = True
    doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor', required=True)  # — Many2one, required = True
    appointment_date = fields.Date(default=fields.Date.today, required=True)  # — Date, required = True, default = today
    doctor_shift_date = fields.Date()  # — Date
    active = fields.Boolean(default=True)  # — Boolean, default = True

    @api.onchange('appointment_date', 'doctor_shift_date')
    def _onchange_doctor_shift_date(self):
        if self.doctor_shift_date and self.appointment_date and self.doctor_shift_date < self.appointment_date:
            return {
                'warning': {
                    'title': 'Невірна дата',
                    'message': 'Дата зміни лікаря не може бути раніше ніж дата призначення',
                },
            }
        return None

    @api.constrains('appointment_date', 'doctor_shift_date')
    def _check_doctor_shift_date(self):
        for record in self:
            if (
                record.doctor_shift_date
                and record.appointment_date
                and record.doctor_shift_date < record.appointment_date
            ):
                raise ValidationError('Дата зміни лікаря не може бути раніше ніж дата призначення')

    @api.depends('patient_id', 'doctor_id', 'doctor_id.category_id.name', 'appointment_date')
    def _compute_display_name(self):
        for record in self:
            category = record.doctor_id.category_id.name
            record.display_name = '%s - %s%s %s' % (
                record.patient_id.name or '',
                record.doctor_id.name or '',
                f' ({category})' if category else '',
                fields.Date.to_string(record.appointment_date)
                or '',  # <ПІБ пацієнта> - <ПІБ лікаря> (<Категорія лікаря>) <Дата призначення>
            )
