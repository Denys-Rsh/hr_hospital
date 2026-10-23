from odoo import api, fields, models


class HrHospitalDiseaseReportWizard(models.TransientModel):
    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Hospital disease report wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Лікарі',
        default=lambda self: self._default_active_ids('hr.hospital.doctor'),
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Хвороби',
        default=lambda self: self._default_active_ids('hr.hospital.disease'),
    )

    date_from = fields.Datetime(string='з')
    date_to = fields.Datetime(string='по')

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
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))
        if self.date_from:
            domain.append(('scheduled_datetime', '>=', self.date_from))
        if self.date_to:
            domain.append(('scheduled_datetime', '<=', self.date_to))
        return domain

    discount = fields.Integer(string='Value')

    def action_show_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Звіт по хворобам',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': self._get_visit_domain(),
            'target': 'current',
        }
