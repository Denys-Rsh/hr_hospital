# Upgrade report: hr_hospital 1.0.0 → 1.3.0

Module versions `19.0.3.0.0 → 19.0.3.3.0`. The schema changes and the role of each
migration script are described in [`changelog.rst`](../changelog.rst). This report
records the control numbers and the results of the deliberate failures. It also gives
the commands that reproduce every number below.

## Environment and inputs

| Item | Value |
|---|---|
| Odoo | 19.0 (community, source checkout in `/home/odoo/odoo_course/odoo`) |
| PostgreSQL | 16.15, user `odoo`, local socket (container `odoocourse-ubuntu24`) |
| Baseline | `dumps/unit-7_before.dump`: `pg_dump -Fc` of DB `odoo`, 2026-11-10 10:15 UTC, `hr_hospital` 19.0.3.0.0 |
| Code states | `e2b51db` 3.0.0 · `ee72b63` 3.1.0 · `7d9ae1c` 3.2.0 · `60102f7` 3.3.0 (branch `unit-7`) |
| Script | [`doc/reproduce_upgrade.sh`](reproduce_upgrade.sh): every scenario runs in its own throw-away DB |

Each scenario restores the baseline into a new DB. It exports the code of one commit
with `git archive` into `/tmp/hr_hospital_upgrade_repro/<scenario>/hr_hospital`, then
removes or renames a migration script when the scenario needs it. Then it runs
`odoo-bin -u hr_hospital --stop-after-init` with `--addons-path` pointing at
that copy. The working copy and the main DB `odoo` are never modified.

## 1. Control numbers (baseline 19.0.3.0.0)

| Check | Value |
|---|---|
| patients | **8** |
| `insurance_policy_number` not NULL | **5** (ids 4–8) |
| numeric / non-numeric / blank | **4** (`1`,`2`,`3`,`5`) / **1** (id 7: `AB-1234`) / **0** |
| visits / patients with visits | **17** / **8** |
| visits without `visit_datetime` | **7** (`scheduled_datetime` used instead) |
| expected `first_visit_date` | 1: 2026-01-12, 2: 2026-02-09, 3: 2026-03-16, 4: 2026-11-03, 5: 2026-11-04, 6: 2026-11-07, 7: 2026-11-01, 8: 2026-11-02 |

Expected result after 1.3.0: 4 integer policies (1, 2, 3, 5), `AB-1234` moved to
`policy_note` of id 7, no value lost (4 + 1 = 5), `first_visit_date` filled for 8 of 8
patients and equal to the dates above.

**Happy path** (`happy`, code `60102f7`, all three scripts): exit code **0**, version
**19.0.3.3.0**. Columns: `policy_number int4`, `policy_note varchar`,
`first_visit_date date`. Policies are 1, 2, 3, 5, and id 7 has NULL with note `AB-1234`.
The log shows `id=7: policy 'AB-1234' is not a valid int4`. `first_visit_date`:
**8 filled, 0 mismatched**. All control numbers match.

## Deliberate failures

| # | What was broken | odoo-bin | Version after | Result |
|---|---|---|---|---|
| 2.1 | `migrations/` removed from 3.1.0 code (rename without script) | **0** | 19.0.3.1.0 | `insurance_policy_number` **dropped** (`Deleting …field_hr_hospital_patient__insurance_policy_number`), new empty `policy_number varchar`: **0 of 5** policies left. Silent data loss: the upgrade reports success |
| 3.1 | DB upgraded to 3.1.0, then 3.2.0 code without `19.0.3.2.0/` (Char→Integer without normalization) | **255** | 19.0.3.1.0 (rolled back) | `InvalidTextRepresentation: invalid input syntax for type integer: "AB-1234"` on `ALTER COLUMN … TYPE int4`. Column stays `varchar`, all 8 rows unchanged |
| 4a | 3.3.0 code without `19.0.3.3.0/` (new field, no post script) | **0** | 19.0.3.3.0 | `first_visit_date` filled for **0 of 8** patients (8 mismatched) |
| 4b | `post-10-fill-first-visit-date.py` renamed to `pre-10-…` | **255** | 19.0.3.0.0 (rolled back) | `UndefinedColumn: column "first_visit_date" of relation "hr_hospital_patient" does not exist`. Even the already applied 3.1.0/3.2.0 pre scripts are rolled back: `insurance_policy_number varchar` is still there |

Conclusions:

* A missing rename script is the most dangerous case: nothing fails, and the data is
  gone.
* A missing type-cleanup script stops the upgrade, but the whole upgrade runs in one
  transaction, so the DB stays consistent.
* Pre vs post matters. A rename or cleanup must happen before the ORM touches the
  schema. Filling a new column is only possible after the ORM has created it.

## How to reproduce

Prerequisites: Docker. Use the project compose file (service `ubuntu`, container
`odoocourse-ubuntu24`, home volume `./home/odoo:/home/odoo`). Odoo 19.0 must be in
`/home/odoo/odoo_course/odoo` with its venv in `/home/odoo/odoo_course/venv`, and
this repository must be in `/home/odoo/odoo_course/custom_addons/hr_hospital`.

```bash
docker compose up -d
```

```bash
docker exec -it -u odoo odoocourse-ubuntu24 bash
```

Inside the container:

```bash
cd /home/odoo/odoo_course/custom_addons/hr_hospital && git fetch && git checkout unit-7
```

```bash
cd /home/odoo/odoo_course && bash custom_addons/hr_hospital/doc/reproduce_upgrade.sh 2>&1 | tee /tmp/upgrade_repro.txt
```

The script runs the scenarios `baseline happy s21 s31 s4a s4b` in this order and prints
the version, columns and control queries for each. You can pass scenario names to run
only those, for example `... reproduce_upgrade.sh s31 s4b`. The full Odoo logs are in
`/tmp/hr_hospital_upgrade_repro/<scenario>.log`. The temporary DBs `u7r_<scenario>` are
dropped at the end; set `KEEP_DBS=1` to keep them for inspection. Each scenario takes
about 5 s.

The same steps by hand, using scenario 3.1 as the example:

```bash
cd /home/odoo/odoo_course && source venv/bin/activate
createdb u7r_s31 && pg_restore --no-owner -d u7r_s31 custom_addons/hr_hospital/dumps/unit-7_before.dump
mkdir -p /tmp/r/a/hr_hospital /tmp/r/b/hr_hospital
git -C custom_addons/hr_hospital archive ee72b63 | tar -x -C /tmp/r/a/hr_hospital
git -C custom_addons/hr_hospital archive 7d9ae1c | tar -x -C /tmp/r/b/hr_hospital
rm -r /tmp/r/b/hr_hospital/migrations/19.0.3.2.0
odoo/odoo-bin -d u7r_s31 --addons-path=odoo/addons,/tmp/r/a -u hr_hospital --stop-after-init --no-http
odoo/odoo-bin -d u7r_s31 --addons-path=odoo/addons,/tmp/r/b -u hr_hospital --stop-after-init --no-http; echo "exit=$?"
psql -d u7r_s31 -c "SELECT latest_version FROM ir_module_module WHERE name='hr_hospital'"
dropdb u7r_s31
```

For the other scenarios, change the commit and the migration file that you remove or
rename, as listed in the failure table. The control queries are the `q` calls in
`doc/reproduce_upgrade.sh`. To check the final module on the main DB, run:

```bash
cd /home/odoo/odoo_course && odoo/odoo-bin -c config/odoo.conf -u hr_hospital --stop-after-init
```
