# Validation Report
## Course Demand Forecasting & Faculty Allocation System

### 1. Purpose

This report documents the validation checks performed on the synthetic academic planning dataset, forecasting pipeline, section allocation results and MySQL database.

### 2. Test environment

- Database: MySQL 8.0.46
- Python: Python 3.x
- Dataset scale: Full
- Random seed: 20261022
- Target academic term: 2027S1
- Data provenance: Fully synthetic; no personal or external data.

### 3. Full-scale dataset

| Entity | Records |
|---|---:|
| Program | 100 |
| Course | 1,000 |
| Prerequisite | 76 |
| StudentPlan | 20,000 |
| StudentCourseHistory | 1,497 |
| RegistrationInterest | 47,467 |
| Faculty | 500 |
| FacultySkill | 1,500 |
| Availability | 2,500 |
| Room | 200 |

### 4. Pipeline execution results

| Metric | Result |
|---|---:|
| Forecast students | 15,277 |
| Allocated students | 15,277 |
| Unmet students | 0 |
| Allocation rate | 100% |
| Sections proposed | 1,016 |
| Faculty assignments | 1,016 |
| Validation status | PASS |

### 5. Validation checks

The following checks were performed:

| Validation | Result |
|---|---|
| Primary-key uniqueness through database primary keys | Enforced |
| Foreign-key referential integrity | Enforced by defined foreign keys |
| ENUM value restrictions | Enforced by MySQL |
| Self-referencing prerequisite prevention | Enforced by CHECK constraint |
| Duplicate course/prerequisite pairs | Enforced by UNIQUE constraint |
| Section enrollment not exceeding section capacity | Enforced by CHECK constraint |
| Room/term/time-slot uniqueness | Enforced by UNIQUE constraint |
| Duplicate section/faculty assignment pairs | Enforced by UNIQUE constraint |
| Unassigned sections in generated allocation | 0 |
| Section capacity violations in database checks | 0 |
| Duplicate assignments in database checks | 0 |

### 6. Automated validation summary

The full-scale execution generated the following validation summary. The current allocator additionally validates StudentCourseHistory primary keys, course references, synthetic student references, grade and term values, prerequisite completion before the planned course, and consistency between linked target-term RegistrationInterest and StudentPlan records:

- Status: PASS
- Error count: 0
- Section count: 1,016
- Assignment count: 1,016
- Unmet-demand rows: 0

### 7. Database verification

The generated full-scale data was imported into MySQL successfully.

Verified database counts included:

- Program: 100
- Course: 1,000
- StudentPlan: 20,000
- Section: 1,016
- WorkloadAssignment: 1,016
- PlanningEvent: 2,032
- StudentCourseHistory: 1,497
- RegistrationInterest: 47,467
- UnmetDemand: 0

### 8. Limitations

The validation results establish consistency for the generated synthetic dataset and the checks listed above. They do not prove that the forecast will achieve 100% allocation in a real university.

Not every possible business rule is enforced by a database constraint. Lifecycle transition sequences, effective-date ordering, history-to-prerequisite checks and some workload rules rely on application-level validation. The allocation event CSV currently records proposal events; it does not demonstrate a complete approval/rejection/cancellation workflow.

### 9. Conclusion

The full-scale synthetic dataset was generated, processed, allocated and imported into MySQL. The recorded pipeline validation status was PASS, with zero reported validation errors and no violations in the specified database integrity checks.