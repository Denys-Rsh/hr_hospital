from freezegun import freeze_time

from odoo.tests import tagged

from .common import HrHospitalCommon


@tagged('post_install', '-at_install')
class TestHrHospitalPatient(HrHospitalCommon):
    @freeze_time('2026-06-15')
    def test_compute_age(self):
        self.patient.birth_date = '2000-06-16'
        self.assertEqual(self.patient.age, 25)
        self.patient.birth_date = '2000-06-15'
        self.assertEqual(self.patient.age, 26)

    def test_compute_visit_count(self):
        Visit = self.env['hr.hospital.visit']
        Visit.create([
            {'name': 'Visit 1', 'patient_id': self.patient.id, 'doctor_id': self.doctor.id},
            {'name': 'Visit 2', 'patient_id': self.patient.id, 'doctor_id': self.intern.id},
            {'name': 'Visit 3', 'patient_id': self.other_patient.id, 'doctor_id': self.doctor.id},
        ])
        self.assertEqual(self.patient.visit_count, 2)
        self.assertEqual(self.other_patient.visit_count, 1)

    def test_patient_sees_only_own_card(self):
        self.env['hr.hospital.visit'].create([
            {'name': 'Own Visit', 'patient_id': self.patient.id, 'doctor_id': self.doctor.id},
            {'name': 'Foreign Visit', 'patient_id': self.other_patient.id, 'doctor_id': self.doctor.id},
        ])
        Patient = self.env['hr.hospital.patient'].with_user(self.user_patient)
        self.assertEqual(Patient.search([]), self.patient)
        self.assertEqual(Patient.browse(self.patient.id).visit_count, 1)
