# Design Document: Qualitative Observations (Phase 4)

## Overview

This design implements Phase 4 of the Keystone project. It introduces the `qualitative_observations` table and the `QualitativeObservationService` to handle non-quantitative student data. This service adheres to the principle of "teacher-first, internal-only" insights.

## Data Schema

### Phase 4 Entities (New)

```sql
-- Qualitative Observations
CREATE TABLE qualitative_observations (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    class_id TEXT, -- Optional
    subject_id TEXT, -- Optional
    date TEXT NOT NULL, -- ISO 8601 YYYY-MM-DD
    category TEXT NOT NULL, -- e.g., 'Academic', 'Social', 'Behavioral'
    observation_text TEXT NOT NULL,
    intensity TEXT CHECK (intensity IN ('positive', 'neutral', 'concern')), -- Optional
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);
```

## Service Architecture

### QualitativeObservationService

**Interface:**

- `create_observation(student_id, teacher_id, date, category, observation_text, class_id=None, subject_id=None, intensity=None)` -> `observation_id`
- `get_observation(observation_id)` -> `observation_dict`
- `update_observation(observation_id, **fields)` -> `success`
- `delete_observation(observation_id)` -> `success`
- `list_observations(student_id=None, teacher_id=None, category=None, start_date=None, end_date=None)` -> `list[observation_dict]`

### Implementation Notes

1.  **Database Integration**: The `DatabaseService` in `src/database.py` will be updated to include the `qualitative_observations` table in its `_initialize_schema` method.
2.  **Date Handling**: Dates must be validated as YYYY-MM-DD strings.
3.  **Intensity Validation**: The `intensity` field, if provided, must be one of the allowed values.
4.  **Referential Integrity**: 
    - Student deletion cascades to observations.
    - Teacher deletion is restricted if observations exist.
    - Class/Subject deletion sets the corresponding fields to NULL in the observation (since the observation about the student might still be relevant even if the class is removed).

## Data Integrity Rules

- `observation_text` cannot be empty.
- `category` is required to ensure organized retrieval.
- `date` is required for timeline tracking.

## Aggregation & Reporting (Preview)

While Phase 4 is focused on CRUD, the listing capability allows the future Phase 5 (Aggregation & Reporting) to retrieve observations for parent report summaries. These summaries will combine quantitative assessment data (Phase 1) with curated qualitative insights (Phase 4).

---
**End of Phase 4 Design**
