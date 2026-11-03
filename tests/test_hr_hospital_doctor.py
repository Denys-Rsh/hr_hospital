from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import HrHospitalCommon


@tagged('post_install', '-at_install')
class TestHrHospitalDoctor(HrHospitalCommon):
    def test_compute_is_intern(self):
        self.assertTrue(self.intern.is_intern)
        self.assertFalse(self.doctor.is_intern)

        self.intern.category_id = self.category_specialist
        self.assertFalse(self.intern.is_intern)

    def test_compute_doctor_id_cleared_when_not_intern(self):
        self.assertEqual(self.intern.doctor_id, self.doctor)

        self.intern.category_id = self.category_specialist
        self.assertFalse(self.intern.doctor_id)

    def test_check_is_intern_forbids_intern_mentor(self):
        second_intern = self.intern.copy({'name': 'Second Intern', 'doctor_id': False})
        with self.assertRaises(ValidationError):
            second_intern.doctor_id = self.intern
