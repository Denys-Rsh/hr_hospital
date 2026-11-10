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
