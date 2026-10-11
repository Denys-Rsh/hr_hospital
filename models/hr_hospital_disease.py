from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Hospital disease'
    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char(string='Назва', required=True)
    display_name = fields.Char(recursive=True)
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Parent model',
        index=True,
        ondelete='restrict',
    )
    child_ids = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='parent_id',
        string='Child Categories',
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError('You cannot create recursive categories!')

    @api.depends('name', 'parent_id.display_name')
    @api.depends_context('hierarchical_naming')
    def _compute_display_name(self):
        hierarchical = self.env.context.get('hierarchical_naming', True)
        for record in self:
            if hierarchical and record.parent_id:
                record.display_name = f'{record.parent_id.display_name} / {record.name}'
            else:
                record.display_name = record.name
