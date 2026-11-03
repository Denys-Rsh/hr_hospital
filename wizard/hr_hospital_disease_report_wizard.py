from odoo import api, fields, models


class HrHospitalDiseaseReportWizard(models.TransientModel):
    """Wizard that shows visits filtered by doctors, diseases and period."""

    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Hospital disease report wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
        default=lambda self: self._default_active_ids('hr.hospital.doctor'),
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases',
        default=lambda self: self._default_active_ids('hr.hospital.disease'),
    )

    date_from = fields.Datetime(string='From')
    date_to = fields.Datetime(string='To')

    @api.model
    def _default_active_ids(self, model_name):
        """Take the records selected in the list of model_name as the default value."""
        if self.env.context.get('active_model') == model_name:
            return [fields.Command.set(self.env.context.get('active_ids', []))]
        return False

    def _get_visit_domain(self):
        """Build the visit domain from the wizard filters."""
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
        """Open the filtered list of visits."""
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Disease Report'),
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': self._get_visit_domain(),
            'target': 'current',
        }
