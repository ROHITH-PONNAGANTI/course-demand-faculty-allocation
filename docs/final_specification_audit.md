# Final Specification Audit

## Verified implementation

- Business workflow: synthetic master data, student plans, registration interest, demand forecast, section proposals, faculty assignments and unmet-demand output.
- Full-scale source volumes: 100 programs, 1,000 courses, 500 faculty, 20,000 student plans.
- Historical demand: the generator creates three prior-term registration-interest windows; `forecast()` blends current target-term interest (65%) with a weighted three-term history (35%).
- Deterministic IDs: generated Program, Course, Faculty, Section and WorkloadAssignment identifiers match the requested zero-padded patterns. Section and assignment year prefixes follow the configured target term (2027).
- Historical student completion: `StudentCourseHistory` is generated and loaded through the SQL script.
- Allocation: skill matching, availability, weekly workload, room capacity, room-slot conflicts and faculty-slot conflicts are considered.
- Exception outputs: `evaluation_exceptions.csv` and `ground_truth.csv` are generated separately from baseline source tables.
- Validation: source and allocation referential checks, capacity/workload/skill/availability checks, duplicate checks, date checks and lifecycle-state checks.
- Reproducibility: starter and full generator checks both returned identical SHA-256 file maps across two runs (10 CSV files compared per scale).
- Full pipeline rerun in this audit: 15,277 forecast, 15,277 allocated, 0 unmet, 1,016 sections, 1,016 assignments; validation PASS; five anomaly cases matched their expected labels.

## Corrections made during this audit

- Added validation for StudentCourseHistory primary-key uniqueness, course references, synthetic student references, grade and term values.
- Added a prerequisite check requiring each planned student's required course to have been completed in an earlier term with the minimum grade.
- Added consistency validation between linked target-term RegistrationInterest and StudentPlan records.
- Added checks that PlanningEvent records reference known Section or WorkloadAssignment records.
- Clarified the anomaly report so it does not imply that all five cases are end-to-end tests of the production validator.

## Remaining limitations (do not misrepresent these)

1. The five anomaly tests are isolated synthetic checks. They do not each invoke the production validator against a corrupted database transaction.
2. PlanningEvent currently records initial proposal events from the allocation run. A complete actor-driven approval, rejection and cancellation workflow is not implemented.
3. The SQL PlanningEvent table has a timestamp default, but the generated PlanningEvent CSV does not explicitly carry event timestamps. MySQL supplies its default when loading.
4. The forecasting model is a transparent weighted heuristic, not a trained machine-learning model. The historical observations are synthetic.
5. A 100% allocation rate is specific to this generated scenario; it is not evidence of universal optimality or real-world performance.
6. The audit reran the Python generator and allocator, but did not independently execute the MySQL import in this environment. The SQL load script and schema were inspected; previously recorded database-import results remain project-provided evidence.

## Reproducibility commands

From the project root:

```powershell
python src/reproducibility_check.py --scale starter
python src/reproducibility_check.py --scale full
```

## Full pipeline command

```powershell
python -m src.allocate
```

## Additional implementation completed in this revision

- Added `src/business_rules.py` with reusable checks for skill eligibility, availability, workload, room/section capacity, prerequisite chronology, duplicate faculty-section assignments and permitted lifecycle transitions.
- Added eight unit tests in `tests/test_business_rules.py`, including valid assignment, all five required exception categories across focused rule tests, valid/invalid transitions and append-only event-history behavior.
- Added `src/forecast_backtest.py`, a rolling-origin backtest that predicts each historical test term from earlier terms only and reports MAE, RMSE and WAPE. The latest full synthetic run evaluated 2,946 course-term observations across 2025S2, 2026S1 and 2026S2: MAE 1.5723, RMSE 2.6057 and WAPE 31.64%. These are synthetic interest-count metrics, not actual enrollment accuracy.
- Added SQL triggers that reject UPDATE and DELETE on PlanningEvent, enforcing append-only event storage at the database layer.
- Expanded the data dictionary with a field-level catalogue of requiredness, uniqueness, domains, units and validation rules.

## Remaining limitations after this revision

1. The five exception fixtures produced by the allocator are still not full transaction-level tests against a live MySQL database. The new reusable Python business-rule functions are directly unit-tested, but the allocator's original anomaly report remains an isolated synthetic evaluation.
2. The append-only event mechanism and transition helper are implemented, but there is no interactive role-based web application or full approval UI. Events can be appended through the helper; the allocator itself still emits proposal events only.
3. Forecast backtesting is against synthetic registration-interest counts. Real enrollment data would be required to make claims about operational forecast accuracy.
4. SQL triggers are included in `schema.sql`; they require a MySQL 8.0+ schema setup to be applied. The Python tests do not execute MySQL triggers.
5. Skill matching currently derives the required skill from course-name keywords. A production system should store a normalized required-skill relationship on Course rather than infer it from titles.
