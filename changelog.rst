=========
Changelog
=========

Upgrade 1.0.0 -> 1.3.0 (19.0.3.0.0 -> 19.0.3.3.0)
=================================================

Versions below are written in full Odoo form; ``1.x.0`` is the module part
of the version (``19.0.3.x.0``). All schema changes concern the
``hr.hospital.patient`` model (table ``hr_hospital_patient``). Every step
has its own migration script in ``migrations/<version>/``; an upgrade from
any earlier version runs all scripts newer than the installed version, in
order. Test results and the commands to reproduce them are in
``doc/UPGRADE_REPORT.md``.

Schema changes
--------------

==============  ===============================  =====================================
Version         Field / column                   Change
==============  ===============================  =====================================
19.0.3.0.0      ``insurance_policy_number``      ``Char(size=20)`` -> ``varchar(20)``
                                                 (starting point)
19.0.3.1.0      ``policy_number``                renamed from ``insurance_policy_number``,
                                                 still ``Char`` / ``varchar``
19.0.3.2.0      ``policy_number``                ``Char`` -> ``Integer`` (``int4``)
19.0.3.2.0      ``policy_note``                  new ``Char`` (``varchar``): keeps
                                                 policy values that are not valid
                                                 integers
19.0.3.3.0      ``first_visit_date``             new ``Date``: date of the earliest
                                                 visit of the patient
==============  ===============================  =====================================

Views: the patient list and form show ``policy_number`` without thousands
separators, ``policy_note`` only when it is set, and ``first_visit_date``.

Migration scripts
-----------------

``19.0.3.1.0/pre-10-rename-policy-number.py``
    Renames the column ``insurance_policy_number`` to ``policy_number`` and
    the matching ``ir_model_fields`` record and XML id. Pre, because the ORM
    must not see the old field as removed: without the script the old column
    is dropped and all policy numbers are lost.

``19.0.3.2.0/pre-10-normalize-policy-number.py``
    Sets blank policy numbers to ``NULL`` and moves values that are not
    digits or do not fit in ``int4`` to the new ``policy_note`` column,
    logging each moved row. Pre, because the ORM casts the column to
    ``int4`` right after pre scripts: without the script the cast fails on
    ``'AB-1234'`` and the upgrade is rolled back.

``19.0.3.3.0/post-10-fill-first-visit-date.py``
    Fills ``first_visit_date`` from the earliest ``visit_datetime`` (or
    ``scheduled_datetime``) of each patient's visits. Post, because the
    column is created by the ORM: as a pre script it fails with "column does
    not exist"; without it the field stays empty for all existing patients.

19.0.3.0.0 (2026-11-03)
=======================

* Added user groups Patient, Intern, Doctor, Manager and Administrator.
* Added access rights and record rules for visits, patients and doctor
  change history.
* Added Ukrainian translation.
* Added tests for doctors, patients and visits.
* Added module documentation: ``static/description/index.html``,
  ``README.rst`` and ``changelog.rst``, the icon and the banner.
* Added docstrings to classes and methods.
* Filled in summary, description, category and images in
  ``__manifest__.py``.

19.0.2.0.0 (2026-10-29)
=======================

* Added the printable doctor report.

19.0.1.0.0 (2026-10-23)
=======================

* Added models for doctors, doctor categories, patients, visits, diseases
  and doctor change history.
* Added views and menus.
* Added wizards for mass reassignment of the personal doctor, visit report
  and disease report.
* Added a scheduled action and a server action that cancel overdue visits.
* Added demo data.
