from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class HrHospitalVisitReportWizard(models.TransientModel):
    _name = 'hr.hospital.visit.report.wizard'
    _description = 'Hospital visit report wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Лікарі',
        default=lambda self: self._default_active_ids('hr.hospital.doctor'),
    )
    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Пацієнти',
        default=lambda self: self._default_active_ids('hr.hospital.patient'),
    )
    date_from = fields.Date(string='Початок періоду')
    date_to = fields.Date(string='Кінець періоду')
    only_completed = fields.Boolean(string='Лише завершені візити')
    disease_id = fields.Many2one(comodel_name='hr.hospital.disease', string='Хвороба')

    @api.model
    def _default_active_ids(self, model_name):
        if self.env.context.get('active_model') == model_name:
            return [fields.Command.set(self.env.context.get('active_ids', []))]
        return False

    def _get_visit_domain(self):
        self.ensure_one()
        domain = []
        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))
        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))
        if self.only_completed:
            domain.append(('status', '=', 'completed'))
        if self.disease_id:
            domain.append(('disease_id', '=', self.disease_id.id))
        if self.date_from:
            domain += [
                '|',
                ('visit_datetime', '>=', self.date_from),
                '&',
                ('visit_datetime', '=', False),
                ('scheduled_datetime', '>=', self.date_from),
            ]
        if self.date_to:
            date_to_next = self.date_to + timedelta(days=1)
            domain += [
                '|',
                ('visit_datetime', '<', date_to_next),
                '&',
                ('visit_datetime', '=', False),
                ('scheduled_datetime', '<', date_to_next),
            ]
        return domain

    def action_show_report(self):
        self.ensure_one()
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError('Початок періоду не може бути пізніше за кінець періоду.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Звіт по візитах',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': self._get_visit_domain(),
            'target': 'current',
        }
