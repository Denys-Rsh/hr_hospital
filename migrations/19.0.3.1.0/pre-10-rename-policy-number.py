import logging

from odoo.tools.sql import column_exists, rename_column

_logger = logging.getLogger(__name__)

TABLE = 'hr_hospital_patient'
MODEL = 'hr.hospital.patient'
OLD = 'insurance_policy_number'
NEW = 'policy_number'


def migrate(cr, version):
    if not version:
        return
    if not column_exists(cr, TABLE, OLD) or column_exists(cr, TABLE, NEW):
        _logger.info('%s.%s: nothing to rename', TABLE, OLD)
        return

    rename_column(cr, TABLE, OLD, NEW)

    cr.execute(
        'UPDATE ir_model_fields SET name = %s WHERE model = %s AND name = %s',
        (NEW, MODEL, OLD),
    )
    cr.execute(
        """
        UPDATE ir_model_data
           SET name = %s
         WHERE module = 'hr_hospital'
           AND model = 'ir.model.fields'
           AND name = %s
        """,
        (f'field_hr_hospital_patient__{NEW}', f'field_hr_hospital_patient__{OLD}'),
    )
    _logger.info('Renamed %s.%s -> %s', TABLE, OLD, NEW)
