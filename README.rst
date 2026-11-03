===========
HR Hospital
===========

Training module for Odoo 19 that manages the daily work of a small clinic:
doctors and interns, patients, visits, a disease catalogue and the history
of personal doctor changes.

The module lives in the root of the repository, so cloning it creates the
``hr_hospital`` directory whose name matches the technical name of the module.

.. contents::
   :local:

Features
========

* Doctors with categories, mentors for interns and a printable doctor report.
* Patients with blood type, age, insurance policy, personal doctor and a
  visit counter with a smart button.
* Visits with status tracking in the chatter and list, form and calendar
  views. Completed visits cannot be edited or deleted.
* Hierarchical disease catalogue with ``Parent / Child`` display names.
* History of personal doctor changes for every patient.
* Wizards: mass reassignment of the personal doctor, visit report and
  disease report.
* A scheduled action and a server action that cancel overdue visits.
* Five user groups with access rights and record rules.
* Ukrainian translation.

Models
======

The module defines 7 models and 3 wizards.

Models:

* ``hr.hospital.medic.info`` - abstract model with blood type, gender,
  birth date and age, shared by doctors and patients.
* ``hr.hospital.doctor`` - doctor or intern.
* ``hr.hospital.doctor.category`` - doctor category (e.g. intern).
* ``hr.hospital.patient`` - patient.
* ``hr.hospital.visit`` - visit of a patient to a doctor.
* ``hr.hospital.disease`` - disease, organised as a tree.
* ``hr.hospital.doctor.history`` - history of personal doctor changes.

Wizards:

* ``hr.hospital.mass.reassign.doctor.wizard`` - assigns a new personal
  doctor to the selected patients.
* ``hr.hospital.visit.report.wizard`` - filters visits by doctors, patients,
  period, status and disease.
* ``hr.hospital.disease.report.wizard`` - filters visits by doctors,
  diseases and period.

Installation
============

1. Put the ``hr_hospital`` directory into one of the paths listed in
   ``addons_path``.
2. Update the list of apps and install **Hr hospital**.

The module depends only on ``base`` and ``mail``.

Usage
=====

1. Open the **Hospital** menu.
2. Create doctor categories, doctors and patients.
3. Schedule visits from a patient card or from a doctor card
   (quick create button).
4. Use the wizards from the action menu of patients, doctors and diseases
   to build reports or reassign the personal doctor.

Security
========

The module adds five groups: Patient, Intern, Doctor, Manager and
Administrator.

ACL defines which operations a group may perform on a model (for example,
only an administrator can delete), while ``ir.rule`` defines which records
are available to it (a patient sees only own visits, a doctor sees own visits
and the visits of own interns). ACL is checked first and acts as a ceiling;
record rules only narrow the result and never grant new rights.

That is why ``perm_*`` flags mean different things in the two layers: in ACL
they grant the operation, in a record rule they only say for which operations
the rule is checked. For example, ``perm_write=False`` in the patient rule for
visits does not forbid writing, it just disables the rule for writing; the
patient still cannot write because the patient ACL has ``perm_write = 0``.

Tests
=====

The module contains 15 tests in ``tests/``:

* ``test_hr_hospital_doctor.py`` - 3 tests;
* ``test_hr_hospital_patient.py`` - 3 tests;
* ``test_hr_hospital_visit.py`` - 9 tests.

Run them with::

    odoo-bin -c odoo.conf -d <database> -u hr_hospital --test-tags /hr_hospital --stop-after-init

Changelog
=========

See ``changelog.rst``.

Credits
=======

Author
------

* Denys Rsh

License
-------

OPL-1
