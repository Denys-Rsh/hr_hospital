from odoo.tests.common import TransactionCase, new_test_user


class HrHospitalCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_intern = cls.env.ref('hr_hospital.hr_hospital_doctor_category_1')
        cls.category_specialist = cls.env.ref('hr_hospital.hr_hospital_doctor_category_2')

        cls.user_patient = new_test_user(cls.env, login='test_patient', groups='hr_hospital.hr_hospital_patient_group')
        cls.user_intern = new_test_user(cls.env, login='test_intern', groups='hr_hospital.hr_hospital_intern_group')
        cls.user_doctor = new_test_user(cls.env, login='test_doctor', groups='hr_hospital.hr_hospital_doctor_group')
        cls.user_manager = new_test_user(cls.env, login='test_manager', groups='hr_hospital.hr_hospital_manager_group')
        cls.user_admin = new_test_user(
            cls.env, login='test_admin', groups='hr_hospital.hr_hospital_administrator_group'
        )

        medic_info = {'blood_type': 'a_positive', 'gender': 'male', 'birth_date': '1980-01-01'}
        cls.doctor = cls.env['hr.hospital.doctor'].create({
            **medic_info,
            'name': 'Test Doctor',
            'category_id': cls.category_specialist.id,
            'user_id': cls.user_doctor.id,
        })
        cls.intern = cls.env['hr.hospital.doctor'].create({
            **medic_info,
            'name': 'Test Intern',
            'category_id': cls.category_intern.id,
            'doctor_id': cls.doctor.id,
            'user_id': cls.user_intern.id,
        })
        cls.other_doctor = cls.env['hr.hospital.doctor'].create({
            **medic_info,
            'name': 'Other Doctor',
            'category_id': cls.category_specialist.id,
        })
        cls.patient = cls.env['hr.hospital.patient'].create({
            **medic_info,
            'name': 'Test Patient',
            'user_id': cls.user_patient.id,
        })
        cls.other_patient = cls.env['hr.hospital.patient'].create({**medic_info, 'name': 'Other Patient'})
