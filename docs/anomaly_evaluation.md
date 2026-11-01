# Anomaly Evaluation Report
## Course Demand Forecasting & Faculty Allocation System

### 1. Purpose

This report documents the evaluation of five deliberately constructed anomaly scenarios in the synthetic academic planning and faculty allocation workflow.

The objective was to exercise five isolated, synthetic rule checks against expected issue labels. These checks operate on copied or constructed test records; they do not inject corrupt rows into the production allocation outputs or prove that every production validator path rejects the same records.

### 2. Evaluation dataset

- Dataset scale: Full
- Random seed: 20261022
- Target term: 2027S1
- Data provenance: Fully synthetic
- Anomaly test cases: 5

### 3. Evaluation results

| Metric | Result |
|---|---:|
| Total test cases | 5 |
| Anomalies detected | 5 |
| Anomalies missed | 0 |
| False positives | 0 |
| Evaluation status | PASS |

### 4. Anomaly scenarios

The project specification identifies the following five important failure conditions:

| No. | Anomaly scenario | Expected system response |
|---|---|---|
| 1 | Faculty assigned outside their teaching-skill eligibility | Detect and reject the invalid assignment |
| 2 | Faculty workload exceeds the permitted limit | Detect the workload violation |
| 3 | Section demand exceeds available room or section capacity | Detect the capacity violation |
| 4 | Student plans a course before completing its prerequisite | Detect the prerequisite violation |
| 5 | Duplicate faculty assignment to the same section | Detect the duplicate assignment |

### 5. Evaluation outcome

The automated anomaly evaluation reported:

- Total test cases: 5
- Detected: 5
- Missed: 0
- False positives: 0
- Status: PASS

This represents successful detection across the five evaluated synthetic test cases.

### 6. Interpretation

The results demonstrate that five isolated test checks matched their expected issue labels under the synthetic evaluation setup. They should not be described as five end-to-end production-validator rejection tests.

A zero-missed and zero-false-positive result on five test cases is useful evidence of rule handling, but it is not sufficient to establish comprehensive production reliability. More test cases, boundary-value testing and real institutional data would be required for that conclusion.

### 7. Limitations

- The test scenarios are synthetic and intentionally constructed.
- Five test cases do not cover every possible combination of academic planning constraints.
- The evaluation does not establish real-world forecasting accuracy.
- The workload and capacity cases use direct arithmetic rule checks; the prerequisite case uses a synthetic completion term; the duplicate case checks a repeated section/faculty pair.
- The production validator independently checks baseline allocation constraints, but the anomaly evaluator does not invoke the production validator separately for every injected case.
- The results should be interpreted as rule-detection evidence, not as proof of a production-ready optimization system.

### 8. Conclusion

The anomaly evaluation completed with PASS status. All five evaluated anomaly cases were detected, with zero missed cases and zero false positives in the reported test run.