from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged

from .common import HrHospitalCommon


@tagged('post_install', '-at_install')
class TestHrHospitalVisit(HrHospitalCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = fields.Datetime.now()
        Visit = cls.env['hr.hospital.visit']
        cls.visit_overdue = Visit.create({
            'name': 'Overdue',
            'patient_id': cls.patient.id,
            'doctor_id': cls.intern.id,
            'scheduled_datetime': now - timedelta(days=1),
        })
        cls.visit_future = Visit.create({
            'name': 'Future',
            'patient_id': cls.patient.id,
            'doctor_id': cls.doctor.id,
            'scheduled_datetime': now + timedelta(days=1),
        })
        cls.visit_other = Visit.create({
            'name': 'Other',
            'patient_id': cls.other_patient.id,
            'doctor_id': cls.other_doctor.id,
            'scheduled_datetime': now - timedelta(days=2),
        })
        cls.visit_completed = Visit.create({
            'name': 'Completed',
            'patient_id': cls.patient.id,
            'doctor_id': cls.doctor.id,
            'scheduled_datetime': now - timedelta(days=3),
        })
        # Статус ставимо окремим write, бо створення завершеного візиту блокує _check_fields.
        cls.visit_completed.status = 'completed'
        cls.visits = cls.visit_overdue | cls.visit_future | cls.visit_other | cls.visit_completed

    def test_action_cancel_overdue_visits(self):
        cancelled = self.visits.action_cancel_overdue_visits()

        self.assertEqual(cancelled, self.visit_overdue | self.visit_other)
        self.assertEqual(self.visit_overdue.status, 'cancelled')
        self.assertEqual(self.visit_other.status, 'cancelled')
        self.assertEqual(self.visit_future.status, 'scheduled')
        self.assertEqual(self.visit_completed.status, 'completed')

    def test_cron_cancel_overdue_visits(self):
        cancelled = self.env['hr.hospital.visit']._cron_cancel_overdue_visits()

        self.assertIn(self.visit_overdue, cancelled)
        self.assertNotIn(self.visit_future, cancelled)
        self.assertNotIn(self.visit_completed, cancelled)
        self.assertEqual(self.visit_overdue.status, 'cancelled')

    def test_check_fields_completed_visit_is_locked(self):
        with self.assertRaises(ValidationError):
            self.visit_completed.doctor_id = self.other_doctor
        # Незавершений візит змінювати можна.
        self.visit_future.doctor_id = self.other_doctor
        self.assertEqual(self.visit_future.doctor_id, self.other_doctor)

    def test_unlink_except_visited(self):
        Visit = self.env['hr.hospital.visit'].with_user(self.user_admin)
        with self.assertRaises(UserError):
            Visit.browse(self.visit_completed.id).unlink()

        Visit.browse(self.visit_future.id).unlink()
        self.assertFalse(self.visit_future.exists())

    def test_compute_same_disease_visit_count(self):
        disease = self.env['hr.hospital.disease'].create({'name': 'Test Disease'})
        (self.visit_overdue | self.visit_other).disease_id = disease

        self.assertEqual(self.visit_overdue.same_disease_visit_count, 2)
        self.assertEqual(self.visit_future.same_disease_visit_count, 0)

    def test_patient_sees_only_own_visits(self):
        visits = self.env['hr.hospital.visit'].with_user(self.user_patient).search([])
        self.assertEqual(visits, self.visit_overdue | self.visit_future | self.visit_completed)

        with self.assertRaises(AccessError):
            visits.browse(self.visit_future.id).write({'name': 'Changed by patient'})

    def test_intern_edits_only_own_visits(self):
        Visit = self.env['hr.hospital.visit'].with_user(self.user_intern)
        self.assertEqual(Visit.search([]), self.visit_overdue)

        Visit.browse(self.visit_overdue.id).write({'name': 'Changed by intern'})
        self.assertEqual(self.visit_overdue.name, 'Changed by intern')

        with self.assertRaises(AccessError):
            Visit.browse(self.visit_future.id).write({'name': 'Changed by intern'})

    def test_doctor_sees_own_and_interns_visits(self):
        visits = self.env['hr.hospital.visit'].with_user(self.user_doctor).search([])
        self.assertEqual(visits, self.visit_overdue | self.visit_future | self.visit_completed)

    def test_manager_cannot_delete_visit(self):
        Visit = self.env['hr.hospital.visit'].with_user(self.user_manager)
        self.assertEqual(Visit.search([]) & self.visits, self.visits)
        with self.assertRaises(AccessError):
            Visit.browse(self.visit_future.id).unlink()
