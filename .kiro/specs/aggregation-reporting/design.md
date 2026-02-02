# Design Document: Aggregation & Reporting (Phase 5)

## Overview

This design implements Phase 5 of the Keystone project. It introduces the `ReportGenerationService`, which aggregates data from Assessments (Phase 1), Averages (Phase 1 Aggregation), and Qualitative Observations (Phase 4) into a structured student progress report.

## Architecture

### ReportGenerationService

The `ReportGenerationService` acts as a facade over existing services, collecting and formatting data specifically for external dissemination.

**Interface:**

- `generate_student_progress_report(student_id, term_id)` -> `dict`
- `list_student_reports_for_class(class_id, term_id)` -> `list[dict]`

### Data Synthesis Logic

1.  **Metadata Retrieval**:
    - Fetch Student, Class, and School details.
    - Fetch Term dates (start_date, end_date).
2.  **Subject-Subject Aggregation**:
    - Identify all `subjects` the student is enrolled in for the given `class`.
    - For each subject:
        - Use `AggregationService` to get the `student_average` and `class_average`.
        - Retrieve `QualitativeObservations` for that student/subject within the term dates.
        - Filter observations by category (e.g., 'Academic', 'Social').
3.  **Report Structure**:
    ```json
    {
      "student_info": { "name": "...", "grade": "...", "class": "..." },
      "term_info": { "name": "...", "start_date": "...", "end_date": "..." },
      "subjects": [
        {
          "subject_name": "Mathematics",
          "average_mark": 78.5,
          "class_average": 72.1,
          "observations": [
             { "date": "...", "category": "...", "text": "..." }
          ]
        }
      ],
      "overall_observations": [] // General student observations (no subject linked)
    }
    ```

## Database Integration

No new tables are required for Phase 5, as it is a pure logic/aggregation layer over existing data.

## Implementation Details

1.  **Service Dependency**: 
    - `ReportGenerationService` requires `DatabaseService` and internally leverages logic from `AggregationService`.
2.  **Date Filtering**: All assessment marks and observations must fall within the `[term.start_date, term.end_date]` range.
3.  **Observation Filtering**: By default, only 'Academic' and 'Social' categories are included in the parent report to avoid sharing internal behavioral notes that might require more nuance in a live setting.

## Verification Plan

1.  **test_phase5_guardrails.py**:
    - Verify that reports only include data from the specified term.
    - Verify that observations from excluded categories (e.g., 'Behavioral') are not present in the default report.
    - Verify that averages match those calculated by the base `AggregationService`.
2.  **example_phase5.py**:
    - Demonstrate generating a full progress report for a student with data from multiple phases.

---
**End of Phase 5 Design**
