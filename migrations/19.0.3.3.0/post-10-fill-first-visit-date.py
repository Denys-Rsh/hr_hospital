"""Fill the new ``first_visit_date`` of existing patients (19.0.3.3.0).

What it does
    Sets ``hr_hospital_patient.first_visit_date`` to the date of the
    earliest visit of each patient, taking ``visit_datetime`` and, for
    visits that have not happened yet, ``scheduled_datetime``. Patients
    without visits keep an empty value. It is a single set-based ``UPDATE``,
    so it does not depend on the ORM or on the number of patients.

Why post-, not pre-
    ``first_visit_date`` is a new stored field, so in a pre script its
    column does not exist yet: the ORM adds it only in ``init_models()``,
    after pre scripts, and the ``UPDATE`` fails with ``UndefinedColumn``.
    A post script is the first point at which the column exists, and all
    data it reads (``hr_hospital_visit``) belongs to this module and is
    already in place. An end script would also work, but it is not needed:
    end scripts wait for every module to be updated, and nothing here
    depends on other modules.

What happens without it
    The upgrade succeeds, but the field is empty for every existing patient
    (0 of 8 filled); only records written after the upgrade would get a
    value. Moving this script to ``pre-`` fails instead: ``column
    "first_visit_date" does not exist``, exit code 255, and the upgrade is
    rolled back to 19.0.3.0.0 (see doc/UPGRADE_REPORT.md, scenario 4).
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE hr_hospital_patient p
           SET first_visit_date = v.first_dt::date
          FROM (SELECT patient_id,
                       MIN(COALESCE(visit_datetime, scheduled_datetime)) AS first_dt
                  FROM hr_hospital_visit
                 WHERE patient_id IS NOT NULL
                 GROUP BY patient_id) v
         WHERE v.patient_id = p.id
           AND v.first_dt IS NOT NULL
    """)
    _logger.info('hr_hospital_patient.first_visit_date: filled for %d patient(s)', cr.rowcount)
