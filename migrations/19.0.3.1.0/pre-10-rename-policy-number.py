"""Rename ``insurance_policy_number`` to ``policy_number`` (19.0.3.1.0).

What it does
    Renames the column ``hr_hospital_patient.insurance_policy_number`` to
    ``policy_number`` in place and renames the matching ``ir_model_fields``
    record and its XML id (``field_hr_hospital_patient__*``), so the field
    keeps its id, its data and everything that references it (views,
    filters, exports, translations).

Why pre-migration
    It must run before the ORM loads the new model. At that point the
    registry still has no ``policy_number`` field, so the ORM has not yet
    created an empty column for it and has not yet removed the field it no
    longer finds in the code. A post script would be too late: by then the
    old column is already gone.

What happens without it
    Odoo sees ``policy_number`` as a brand-new field and creates an empty
    ``varchar`` column. ``insurance_policy_number`` is treated as removed:
    its ``ir.model.fields`` record is deleted and the column is dropped
    together with it. All 5 stored policy numbers are lost and the upgrade
    still reports success (see doc/UPGRADE_REPORT.md, scenario 2.1).

The script is idempotent: it does nothing on a fresh install (``version``
is empty) or when the column has already been renamed.
"""

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
