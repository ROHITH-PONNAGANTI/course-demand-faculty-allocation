# AI-Assisted Development and Prompt History

## 1. Purpose of AI Assistance

AI tools were used as development and review assistants during the design, implementation, debugging, testing, and documentation of the Course Demand Forecasting and Faculty Allocation System.

The objective was to accelerate development, explore implementation approaches, identify potential issues, and improve code quality while retaining responsibility for reviewing and validating the final implementation.

## 2. Areas Where AI Assisted

| Development Area | AI Assistance |
|---|---|
| System Architecture | Discussing entity relationships, system modules, workflow and design decisions |
| Synthetic Data Generation | Developing deterministic data-generation logic and validation approaches |
| Forecasting | Reviewing forecasting assumptions, historical demand and evaluation metrics |
| Faculty Allocation | Developing and reviewing constraint-based allocation logic |
| Database Design | Reviewing MySQL relationships, keys and integrity constraints |
| Business Rule Validation | Identifying validation conditions and negative scenarios |
| Testing | Designing unit tests and anomaly evaluation approaches |
| Documentation | Preparing technical explanations, README and project documentation |

## 3. Where AI Accelerated Development

AI assistance reduced the time required for initial architecture discussions, code structuring, debugging, test-case preparation, SQL review and technical documentation.

It also helped identify potential edge cases and clarify implementation alternatives.

## 4. Where AI Assistance Was Significant

AI assistance was significant during implementation planning and code development. Generated suggestions and code were treated as starting points rather than automatically correct solutions.

The implementation was reviewed through execution, testing and comparison against the defined business requirements.

## 5. Personal Review and Validation

The following development and verification activities were performed:

- Set up and executed the project in a local Python environment.
- Generated the full-scale synthetic dataset.
- Executed the Python test suite and verified all eight tests passed.
- Ran the forecasting and allocation workflow.
- Reviewed allocation validation and anomaly evaluation results.
- Executed forecasting backtesting and reviewed MAE, RMSE and WAPE.
- Verified reproducibility across ten generated files.
- Configured MySQL and imported the generated CSV records.
- Reviewed database structure, relationships and import consistency.
- Reviewed project outputs and technical documentation.

## 6. Limitations of AI Assistance

AI-generated code and recommendations can contain incorrect assumptions, incomplete constraints or implementation errors.

Therefore, suggestions were reviewed against the project requirements and validated through actual execution wherever applicable.

## 7. Representative Prompt History

The following prompts represent the main technical areas addressed during AI-assisted development. They are representative prompts, not a verbatim historical conversation export.

### Prompt 1: System Architecture and Design

Act as a senior software architect. Design an end-to-end Python and MySQL system for academic course demand forecasting and faculty allocation. Identify the entities, relationships, data flow, business rules, constraints, and module responsibilities. Keep the design modular, explainable, and suitable for a reproducible synthetic-data project.

### Prompt 2: Synthetic Data Generation

Design a deterministic synthetic data generator for an academic planning system. Generate realistic relationships between programs, courses, prerequisites, student plans, faculty, skills, availability, and rooms. Use fixed random seeds, valid foreign keys, configurable dataset sizes, and derived values. Explain how to ensure reproducibility.

### Prompt 3: Forecasting Methodology

Act as a data analyst. Review a course demand forecasting approach based on historical registration-interest records. Evaluate the assumptions, identify possible data leakage, recommend an appropriate baseline forecasting method, and explain how to measure performance using MAE, RMSE, and WAPE.

### Prompt 4: Faculty Allocation Algorithm

Develop an explainable faculty allocation algorithm in Python. Consider faculty skills, availability, weekly workload limits, course demand, section capacity, and room constraints. Define allocation priorities, rejection conditions, and unmet-demand handling. Avoid assigning faculty who violate business rules.

### Prompt 5: Business Rule Validation

Review the business rules for an academic course planning system. Identify validation requirements for prerequisite ordering, faculty skill compatibility, workload limits, room capacity, section enrollment, and duplicate assignments. Provide positive and negative test cases for each rule.

### Prompt 6: SQL Database Design Review

Act as a senior MySQL database engineer. Review the relational schema for an academic planning system. Evaluate primary keys, foreign keys, unique constraints, check constraints, relationship cardinality, referential integrity, and transaction handling. Identify business rules that require application-level validation rather than ordinary database constraints.

### Prompt 7: Testing and Anomaly Evaluation

Design a test strategy for a Python-based faculty allocation system. Include unit tests for valid and invalid assignments, prerequisite violations, workload violations, capacity violations, and duplicate assignments. Explain how to measure detected anomalies, missed anomalies, and false positives using separate ground-truth labels.

### Prompt 8: Final Project Audit

Act as a strict technical project evaluator. Audit the complete project against its business requirements. Examine source code, database schema, generated datasets, SQL imports, test results, forecasting metrics, documentation, and reproducibility. Identify missing requirements, unsupported claims, data integrity problems, and unnecessary features. Prioritize only changes essential for submission.

## 8. Ownership and Responsibility

The developer is responsible for understanding, reviewing, explaining and defending the submitted implementation, including its architecture, business rules, assumptions, validation results and limitations.