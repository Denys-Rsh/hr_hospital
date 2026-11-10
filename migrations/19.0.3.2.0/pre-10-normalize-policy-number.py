"""Prepare ``policy_number`` for the Char -> Integer change (19.0.3.2.0).

What it does
    Cleans ``hr_hospital_patient.policy_number`` so that every remaining
    value can be cast to PostgreSQL ``int4``:

    * blank strings become ``NULL``;
    * values that are not digits only, or do not fit in ``int4``
      (> 2147483647), are copied to the new column ``policy_note`` and
      ``policy_number`` is set to ``NULL``. Every such row is logged with
      its id, so nothing disappears silently.

    The column type itself is left as ``varchar``; the ORM converts it when
    it loads the new ``fields.Integer`` definition.

Why pre-migration
    The ORM converts the column with
    ``ALTER TABLE ... ALTER COLUMN policy_number TYPE int4
    USING policy_number::int4`` while it updates the tables. That happens
    after pre scripts and before post scripts, so the data must be clean
    before it, i.e. in a pre script. ``policy_note`` is created here as
    well (with the same type the ORM would give it) because it has to
    receive the values before the conversion.

What happens without it
    The cast fails on the first non-numeric value (``'AB-1234'``):
    ``invalid input syntax for type integer``. The registry fails to load,
    odoo-bin exits with code 255 and the whole upgrade is rolled back; the
    database stays on 19.0.3.1.0 (see doc/UPGRADE_REPORT.md, scenario 3.1).

The script does nothing on a fresh install or when the column is no
longer ``varchar`` (already converted), so it is safe to run twice.
"""

import logging

from odoo.tools.sql import column_exists, create_column, table_columns

_logger = logging.getLogger(__name__)

TABLE = 'hr_hospital_patient'
COLUMN = 'policy_number'
NOTE = 'policy_note'
INT_MAX = 2147483647  # PostgreSQL int4, the column type of fields.Integer


def migrate(cr, version):
    if not version:
        return
    column = table_columns(cr, TABLE).get(COLUMN)
    if not column or column['udt_name'] != 'varchar':
        _logger.info('%s.%s: nothing to normalize', TABLE, COLUMN)
        return

    if not column_exists(cr, TABLE, NOTE):
        create_column(cr, TABLE, NOTE, 'varchar', 'Policy Note')

    cr.execute(f"""
        UPDATE {TABLE} SET {COLUMN} = NULL
         WHERE {COLUMN} IS NOT NULL AND btrim({COLUMN}) = ''
    """)
    blank = cr.rowcount

    cr.execute(f"""
        UPDATE {TABLE}
           SET {NOTE} = {COLUMN}, {COLUMN} = NULL
         WHERE {COLUMN} IS NOT NULL
           AND CASE WHEN btrim({COLUMN}) ~ '^[0-9]+$'
                    THEN btrim({COLUMN})::numeric > %s
                    ELSE TRUE
               END
     RETURNING id, {NOTE}
    """, (INT_MAX,))
    moved = cr.fetchall()

    _logger.info('%s.%s: %d blank value(s) set to NULL', TABLE, COLUMN, blank)
    for rec_id, note in moved:
        _logger.warning('%s id=%s: policy %r is not a valid int4, set to NULL (original kept in %s)',
                        TABLE, rec_id, note, NOTE)
