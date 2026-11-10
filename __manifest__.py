{
    "name": "Hr hospital",
    "summary": "Doctors, patients, visits and diseases of a hospital",
    "description": """
Hospital management
===================
Manages doctors and interns, patients, visits, a hierarchical disease
catalogue and the history of personal doctor changes. Includes wizards
for reports and mass reassignment of the personal doctor, a scheduled
action that cancels overdue visits and five user groups with record rules.
""",
    "author": "Denys Rsh",
    "maintainer": "Denys Rsh",
    "category": "Human Resources",
    "version": "19.0.3.3.0",
    "license": "OPL-1",
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,

    "depends": ["base", "mail"],

    "data": [
        "security/hr_hospital_security.xml",
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
        "demo/hr_hospital_user_demo.xml",
        "demo/hr_hospital_doctor_demo.xml",
        "demo/hr_hospital_patient_demo.xml",
        "demo/hr_hospital_disease_demo.xml",
        "demo/hr_hospital_visit_demo.xml",
    ]
}