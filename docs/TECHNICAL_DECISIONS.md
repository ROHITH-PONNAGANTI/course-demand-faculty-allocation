# Technical Decisions, Assumptions and Limitations

## 1. Problem Definition

Academic institutions need to estimate course demand and allocate faculty, course sections and rooms while respecting prerequisites, faculty skills, availability, workload limits and room capacity.

This project demonstrates a reproducible approach to academic resource planning using Python, MySQL and synthetic institutional data.

## 2. System Design Decisions

| Design Decision | Reason |
|---|---|
| Python | Supports data generation, forecasting, allocation and validation |
| MySQL | Provides relational storage, primary keys and foreign-key constraints |
| Synthetic Data | Enables testing without confidential student or faculty records |
| Fixed Random Seed | Makes dataset generation reproducible |
| Modular Architecture | Separates generation, business rules, forecasting and allocation |
| CSV Data Exchange | Provides a simple interface between Python processing and MySQL bulk loading |
| Ground-Truth Labels | Allows anomaly detection results to be compared against expected outcomes |

## 3. Data Generation Assumptions

The project generates synthetic academic records using a fixed random seed of 20261022.

Full-scale generation includes:

- 100 programs.
- 1,000 courses.
- 500 faculty members.
- 20,000 student plans.

Dependent records are generated using existing parent identifiers to maintain referential consistency.

Derived values are calculated from source records rather than independently randomized.

## 4. Forecasting Methodology

The system uses a weighted heuristic based on current target-term registration interest and the three most recent historical terms.

Historical demand weights:

- Most recent term: 0.50.
- Second most recent term: 0.30.
- Third most recent term: 0.20.

The forecast combines 65 percent current target-term interest with 35 percent weighted historical demand.

Only SUBMITTED and CONFIRMED registration-interest records contribute to current demand.

This method was selected because it is transparent, straightforward to reproduce and easy to explain.

It is a forecasting heuristic rather than a trained machine-learning model.

## 5. Faculty Allocation Decisions

Faculty allocation considers:

- Faculty eligibility and active status.
- Required course skills.
- Faculty availability.
- Weekly workload limits.
- Course demand.
- Section capacity.
- Room availability.
- Duplicate assignment prevention.

The allocation process proposes sections and faculty assignments while recording unmet demand when available resources cannot accommodate the forecast demand.

The implementation uses a planning heuristic and does not guarantee a globally optimal timetable.

## 6. Business Rule Validation

The system validates the following negative scenarios:

1. Faculty assigned outside their qualified skill set.
2. Faculty workload exceeded.
3. Section capacity exceeded.
4. Course scheduled before its prerequisite.
5. Duplicate section assignment.

Positive and negative cases are covered by automated Python unit tests.

Anomaly evaluation uses separate synthetic ground-truth labels to compare expected and detected violations.

## 7. Database Design Decisions

MySQL stores the academic entities and generated planning outputs.

The schema contains 14 tables, including:

- Program
- Course
- Prerequisite
- StudentPlan
- StudentCourseHistory
- RegistrationInterest
- Faculty
- FacultySkill
- Availability
- Room
- Section
- WorkloadAssignment
- PlanningEvent
- UnmetDemand

Primary keys, foreign keys, unique constraints and check constraints support relational consistency.

Some cross-table and aggregate business rules require application-level validation rather than ordinary database constraints.

## 8. Testing and Evaluation Strategy

The project uses:

- Python compilation checks.
- Automated unit tests.
- Allocation validation.
- Synthetic anomaly evaluation.
- Rolling-origin forecasting backtesting.
- Full-scale reproducibility checks.
- MySQL CSV import verification.

Reported Python test results: 8 passed.

Reported anomaly evaluation: 5 detected, 0 missed and 0 false positives.

Reported reproducibility: identical results across 10 compared files.

## 9. Forecasting Evaluation Results

The rolling-origin backtest evaluated 2,946 observations across three synthetic historical terms.

| Metric | Result |
|---|---:|
| MAE | 1.5723 |
| RMSE | 2.6057 |
| WAPE | 31.64% |

These metrics measure performance against synthetic registration-interest counts. They do not establish real-world enrollment forecasting accuracy.

## 10. Design Trade-offs

| Trade-off | Explanation |
|---|---|
| Synthetic instead of real data | Improves reproducibility and avoids confidential records, but limits real-world generalization |
| Weighted heuristic instead of ML | Improves interpretability and reduces model complexity, but may not capture complex demand patterns |
| CSV exchange instead of live DB integration | Simplifies data transfer, but does not support real-time synchronization |
| Constraint-based allocation instead of global optimization | Makes decisions easier to explain, but does not guarantee globally optimal resource utilization |

## 11. Known Limitations

- No live university enrollment integration.
- No trained machine-learning forecasting model.
- No production deployment or administrative dashboard.
- Student-level prerequisite and course progression modelling can be improved.
- Real institutional timetable calendars are not implemented.
- No global timetable optimization.
- Some cross-table business rules are validated in Python rather than enforced directly in MySQL.
- Planning events record proposal creation; a complete approval, rejection and cancellation workflow is outside the current implementation.

## 12. Future Improvements

Potential future improvements include:

- Integration with actual historical enrollment data.
- Forecasting model comparison using real enrollment observations.
- Global timetable optimization using Google OR-Tools.
- Direct Python-to-MySQL integration.
- Institution-specific academic calendars and scheduling slots.
- Approval and lifecycle management workflows.
- Administrative dashboard for reviewing forecasts and allocations.

## 13. Conclusion

The project demonstrates an end-to-end synthetic academic planning workflow combining demand forecasting, faculty allocation, relational database design, business-rule validation, anomaly evaluation and reproducibility.

The implementation prioritizes explainability, deterministic execution and measurable validation over unnecessary system complexity.