{
    "name": "Hr hospital",
    "author": "Denys Rsh",
    "version": "19.0.2.0.0",
    "license": "OPL-1",

    "depends": ["base", "mail"],

    "data": [
        "security/ir.model.access.csv",
        "views/hr_hospital_menu.xml",
        "views/hr_hospital_doctor_views.xml",
        "views/hr_hospital_patient_views.xml",
        "views/hr_hospital_disease_views.xml",
        "views/hr_hospital_visit_views.xml",
        "views/hr_hospital_doctor_category_views.xml",
        "views/hr_hospital_doctor_history_views.xml",
        "data/hr_hospital_disease_data.xml",
        "data/hr_hospital_doctor_category_data.xml",
        "data/hr_hospital_visit_server_action_data.xml",
        "data/hr_hospital_visit_cron_data.xml",
        "wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml",
        "wizard/hr_hospital_visit_report_wizard_view.xml",
        "wizard/hr_hospital_disease_report_wizard_view.xml",
        "report/hr_hospital_doctor_report.xml",
    ],

    "demo": [
        "demo/hr_hospital_doctor_demo.xml",
        "demo/hr_hospital_patient_demo.xml",
        "demo/hr_hospital_disease_demo.xml",
        "demo/hr_hospital_visit_demo.xml",
    ]
}