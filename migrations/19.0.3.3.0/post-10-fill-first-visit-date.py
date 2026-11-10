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
