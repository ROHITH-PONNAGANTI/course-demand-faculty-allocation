# Course Demand Forecasting & Faculty Allocation System

A reproducible Python and MySQL project that forecasts course demand and proposes course sections, room assignments, and faculty allocations under capacity, skill, availability, and workload constraints.

The project uses synthetic institutional data to demonstrate an end-to-end academic resource planning workflow.

## 1. Technology Stack

- **Programming:** Python 3.10+
- **Database:** MySQL 8.0+
- **Data processing:** Python standard library
- **Database loading:** MySQL `LOAD DATA LOCAL INFILE`
- **Reproducibility:** Seed-based synthetic data generation and SHA-256 file comparison

No third-party Python packages are required by the current pipeline.

## 2. Project Architecture

The project follows this workflow:

1. Python generates synthetic institutional data and exports CSV files.
2. The Python allocation pipeline reads the generated CSV data.
3. Demand forecasting estimates student demand for the target term.
4. The allocation process proposes sections, rooms, and faculty assignments.
5. Validation checks identify allocation and data-integrity violations.
6. MySQL stores the generated source data and allocation outputs through CSV bulk import.

**Important:** The current implementation uses CSV files as the interface between Python and MySQL. It does not establish a live Python-to-MySQL connection.

## 3. Requirements

- Python 3.10 or later
- MySQL 8.0 or later for database persistence
- Git (optional, for version control)

## 4. Quick Start

Run the following commands from the project root in Windows PowerShell.

### Create and activate a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Generate starter data and run allocation

```powershell
python src/generate_data.py --scale starter
python src/allocate.py
```

### Generate full-scale data and run allocation

```powershell
python src/generate_data.py --scale full
python src/allocate.py
```

The default random seed is `20261022`. Using the same seed and scale produces reproducible input data.

The starter and full configurations use the same generation rules and database schema.

## 5. MySQL Database Setup

The database schema is available in `sql/schema.sql`, and the bulk-loading script is in `sql/load_csv.sql`.

### Step 1: Create the database and tables

From the project root, run:

```powershell
cmd /c "mysql -u root -p < sql\schema.sql"
```

Enter your MySQL password when prompted.

### Step 2: Enable LOCAL INFILE on the MySQL server

Run:

```powershell
mysql -u root -p -e "SET GLOBAL local_infile = 1;"
```

This requires an account with sufficient administrative privileges. The setting is server-wide and may reset after a MySQL restart.

### Step 3: Import CSV files

Run:

```powershell
cmd /c "mysql --local-infile=1 -u root -p < sql\load_csv.sql"
```

The import script loads source tables before dependent tables and then imports allocation outputs.

Only enable local file loading when you trust the files being imported. You can disable the server setting after importing:

```powershell
mysql -u root -p -e "SET GLOBAL local_infile = 0;"
```

## 6. Main Project Components

| File or folder | Purpose |
|---|---|
| `src/generate_data.py` | Generates synthetic institutional data |
| `src/allocate.py` | Forecasts demand and proposes resource allocations |
| `src/reproducibility_check.py` | Checks output reproducibility using SHA-256 |
| `src/business_rules.py` | Contains reusable business-rule validation functions |
| `src/forecast_backtest.py` | Evaluates forecasting performance on historical synthetic terms |
| `sql/schema.sql` | Defines the MySQL database schema |
| `sql/load_csv.sql` | Imports CSV data into MySQL |
| `config.json` | Stores generation and allocation settings |
| `docs/data_dictionary.md` | Documents dataset fields and tables |
| `data/` | Contains generated source CSV data |
| `outputs/` | Contains forecasts, allocations, and evaluation results |
| `tests/` | Contains automated business-rule tests |

## 7. Forecasting Method

For each course, the pipeline uses the three most recent historical terms with weights:

- Most recent term: 0.50
- Second most recent term: 0.30
- Third most recent term: 0.20

The forecast is calculated as:

```text
Forecast = CEILING(
    0.65 × Target-Term Current Interest
    + 0.35 × Weighted Historical Demand
)
```

Only `SUBMITTED` and `CONFIRMED` registration interest contributes to current demand.

This is a transparent forecasting heuristic, not a trained machine learning model. Actual forecast accuracy requires backtesting against historical enrolment data using metrics such as MAE, RMSE, and WAPE.

## 8. Allocation Rules

The allocation process applies the following constraints:

- Faculty must be active and available during the target term.
- Faculty must possess the required course skill.
- Faculty assignments must respect weekly workload and term availability limits.
- Planned section enrollment cannot exceed the smaller of default section capacity and room capacity.
- Rooms and faculty cannot be double-booked in the same target-term time slot.
- Unserved demand is recorded in the unmet-demand output with a reason code.
- The current implementation assigns one faculty member per section and reserves each room once per target term.

The allocation process uses a planning heuristic rather than a global timetable optimization algorithm.

## 9. Outputs

Important generated files include:

| Output | Description |
|---|---|
| `demand_forecast.csv` | Forecasted demand by course |
| `Section.csv` | Proposed course sections and room assignments |
| `WorkloadAssignment.csv` | Proposed faculty assignments and decision reasons |
| `unmet_demand.csv` | Demand that could not be allocated |
| `PlanningEvent.csv` | Proposal events recording section and faculty decisions |
| `evaluation_exceptions.csv` | Synthetic negative test cases |
| `ground_truth.csv` | Expected labels for anomaly evaluation |
| `anomaly_test_results.csv` | Results of anomaly detection tests |
| `anomaly_evaluation.json` | Anomaly detection evaluation summary |
| `evaluation_metrics.json` | Allocation coverage and evaluation counts |
| `validation_summary.json` | Data-integrity and allocation validation results |

Generated CSV and JSON files are excluded from Git by default. Run the pipeline to recreate them.

## 10. Full-Scale Execution Results

The following results were obtained from the full-scale synthetic dataset.

| Metric | Result |
|---|---:|
| Student plans | 20,000 |
| Forecast students | 15,277 |
| Allocated students | 15,277 |
| Unmet students | 0 |
| Allocation rate | 100% |
| Proposed sections | 1,016 |
| Faculty assignments | 1,016 |
| Validation status | PASS |

Additional verification:

- All 5 synthetic anomaly test cases were detected.
- No missed anomalies or false positives were recorded in those tests.
- No unassigned sections were found.
- No section capacity violations were found.
- No duplicate faculty assignments were found.
- Full-scale reproducibility check returned identical results across 10 compared files.

These results demonstrate that the pipeline works against its generated test data. They do not establish 100% accuracy on real institutional data.

## 11. Anomaly Evaluation

Five synthetic negative cases are evaluated separately:

1. Faculty assigned outside their qualified skill.
2. Faculty workload exceeded.
3. Section capacity exceeded.
4. Prerequisite ordering violation.
5. Duplicate assignment.

These cases are maintained separately from the valid baseline allocation data. The prerequisite anomaly test uses synthetic completion history rather than actual student records.

## 12. Reproducibility

Run the following commands to verify reproducibility:

```powershell
python src/reproducibility_check.py --scale starter
```

For full-scale verification:

```powershell
python src/reproducibility_check.py --scale full
```

The script compares SHA-256 checksums of generated files to check whether repeated runs with the same seed produce identical outputs.

## 13. Limitations and Future Improvements

- Replace synthetic student demand with actual historical enrolment data.
- Backtest forecasting performance using MAE, RMSE, and WAPE.
- Improve student-level prerequisite and course progression modelling.
- Replace synthetic AM/PM slots with institution-specific timetables and calendar dates.
- Introduce global allocation optimization using tools such as Google OR-Tools.
- Develop a direct Python-to-MySQL integration layer if live database interaction is required.
- Improve database import error handling and transaction recovery.
- Add lifecycle transition enforcement and approval workflows.

## 14. Data Disclaimer

All institutional records used in this project are synthetically generated. No personal student or faculty records or external institutional datasets are used.

The project is intended as a reproducible academic resource-planning prototype, not as a production-ready university scheduling system.

## 15. Specification Audit and Implementation Limitations

See [`docs/final_specification_audit.md`](docs/final_specification_audit.md) for a requirement-by-requirement implementation audit, verification evidence and known limitations.

The demand forecast is a weighted heuristic using current target-term interest and three prior synthetic terms; it is not a trained ML model. The anomaly suite contains five isolated synthetic rule checks, not five end-to-end database fault-injection tests. Planning events currently record proposal creation; a complete human approval/rejection workflow is outside the current implementation.

Generated source CSVs are intentionally not committed. Generate them with the documented command before running the pipeline or importing into MySQL. Selected allocation and evaluation outputs are included as demonstration evidence.

## 16. Additional Verification and Evaluation

Run the focused business-rule test suite:

```powershell
python -m unittest discover -s tests -v
```

Run the rolling-origin forecast backtest after generating source data:

```powershell
python src/forecast_backtest.py
```

The backtest reports MAE, RMSE and WAPE across earlier synthetic terms. Each test-term prediction uses only earlier terms; target-term interest is excluded from its own prediction. These metrics measure fit to synthetic registration-interest counts, **not actual student enrollment or real-world forecast accuracy**.

`src/business_rules.py` contains reusable rule checks for skill eligibility, workload, capacity, prerequisite ordering, duplicate assignments and lifecycle transitions. `tests/test_business_rules.py` exercises valid and invalid cases. The append-only SQL triggers on `PlanningEvent` prevent updates and deletes; a new event row is required to record a state change.

## Documentation

- [ER Diagram](docs/ER_Diagram.pdf)
- [Data Dictionary](docs/data_dictionary.md)
- [Validation Report](docs/validation_report.md)
- [Anomaly Evaluation](docs/anomaly_evaluation.md)
- [Specification Audit](docs/final_specification_audit.md)
- [AI-Assisted Development & Prompt Engineering](docs/AI_ASSISTED_DEVELOPMENT.md)