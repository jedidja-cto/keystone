# Design Document: Teacher Core Operations (Phase 1)

## Overview

This design implements Phase 1 of the Keystone project, building upon Phase 0 foundational entities. The system provides CRUD operations for lesson planning and assessment management, plus aggregation logic for class and student averages. Implementation uses Python with SQLite for data persistence.

## Data Schema

### Phase 0 Entities (Foundation)

```sql
-- Schools
CREATE TABLE schools (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    contact_info TEXT
);

-- Grades
CREATE TABLE grades (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    name TEXT NOT NULL,
    ordinal INTEGER,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, name)
);

-- Teachers
CREATE TABLE teachers (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
);

-- Students
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    enrollment_status TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
);

-- Subjects
CREATE TABLE subjects (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, name)
);

-- Classes
CREATE TABLE classes (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    grade_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
);

-- Student-Class enrollment (many-to-many)
CREATE TABLE student_classes (
    student_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    PRIMARY KEY (student_id, class_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Teacher-Class assignment (many-to-many)
CREATE TABLE teacher_classes (
    teacher_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    PRIMARY KEY (teacher_id, class_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Class-Subject mapping (many-to-many)
CREATE TABLE class_subjects (
    class_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    PRIMARY KEY (class_id, subject_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Academic Calendar
CREATE TABLE terms (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    CHECK (start_date < end_date)
);

CREATE TABLE teaching_days (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, date)
);

CREATE TABLE holidays (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE(school_id, date)
);

CREATE TABLE exam_periods (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    CHECK (start_date < end_date)
);
```

### Phase 1 Entities (New)

```sql
-- Lesson Plans
CREATE TABLE lesson_plans (
    id TEXT PRIMARY KEY,
    teacher_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    instructional_notes TEXT,
    topic TEXT,
    reference_materials TEXT,
    duration TEXT,
    status TEXT NOT NULL CHECK (status IN ('draft', 'finalized')),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Assessments
CREATE TABLE assessments (
    id TEXT PRIMARY KEY,
    teacher_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    date TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    maximum_marks REAL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Assessment Marks
CREATE TABLE assessment_marks (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    value REAL NOT NULL CHECK (value >= 0),
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(assessment_id, student_id)
);
```

## Service Architecture

### Core Services

**Database Service**
- Manages SQLite connection
- Executes queries with parameter binding
- Handles transactions

**LessonPlanService**
- `create_lesson_plan(teacher_id, class_id, subject_id, status, instructional_notes=None, **optional_fields)` → lesson_plan_id
- `get_lesson_plan(lesson_plan_id)` → lesson_plan_dict
- `update_lesson_plan(lesson_plan_id, **fields)` → success
- `delete_lesson_plan(lesson_plan_id)` → success
- `list_lesson_plans(teacher_id=None, class_id=None, subject_id=None)` → list[lesson_plan_dict]

**AssessmentService**
- `create_assessment(teacher_id, class_id, subject_id, date, name, **optional_fields)` → assessment_id
- `get_assessment(assessment_id)` → assessment_dict
- `update_assessment(assessment_id, **fields)` → success
- `delete_assessment(assessment_id)` → success
- `list_assessments(teacher_id=None, class_id=None, subject_id=None)` → list[assessment_dict]

**AssessmentMarkService**
- `create_mark(assessment_id, student_id, value)` → mark_id
  - Validates: student enrolled in assessment's class
  - Validates: value <= maximum_marks (if defined)
  - Validates: no duplicate (assessment_id, student_id)
- `get_mark(mark_id)` → mark_dict
- `update_mark(mark_id, value)` → success
  - Validates: value <= maximum_marks (if defined)
- `delete_mark(mark_id)` → success
- `list_marks(assessment_id=None, student_id=None)` → list[mark_dict]

**AggregationService**
- `calculate_class_average(assessment_id)` → float | None
  - Query: `SELECT AVG(value) FROM assessment_marks WHERE assessment_id = ?`
  - Returns None if no marks exist
- `calculate_student_average(student_id, class_id, subject_id)` → float | None
  - Query: Join assessments with assessment_marks filtered by class_id, subject_id, student_id
  - Compute: `SELECT AVG(value) FROM assessment_marks WHERE student_id = ? AND assessment_id IN (SELECT id FROM assessments WHERE class_id = ? AND subject_id = ?)`
  - Returns None if no marks exist
- `generate_export_summary(class_id, subject_id, start_date=None, end_date=None)` → export_summary_dict
  - Returns: {
      "class_metadata": {...},
      "subject_metadata": {...},
      "assessments": [
        {
          "id": "...",
          "name": "...",
          "date": "...",
          "maximum_marks": ...,
          "class_average": ...
        }
      ],
      "students": [
        {
          "id": "...",
          "first_name": "...",
          "last_name": "...",
          "student_average": ...,
          "marks": [
            {"assessment_id": "...", "value": ...}
          ]
        }
      ]
    }

## Aggregation Logic

### Class Average Calculation
- **Trigger**: On-demand via `calculate_class_average(assessment_id)`
- **Logic**: Arithmetic mean of all marks for the assessment
- **Exclusions**: Students with no mark entry are excluded
- **Null handling**: Returns None when no marks exist

### Student Average Calculation
- **Trigger**: On-demand via `calculate_student_average(student_id, class_id, subject_id)`
- **Logic**: Arithmetic mean of all marks for the student in the specified class/subject
- **Exclusions**: Assessments where student has no mark entry are excluded
- **Null handling**: Returns None when no marks exist

### Export Summary Generation
- **Trigger**: On-demand via `generate_export_summary(class_id, subject_id, start_date, end_date)`
- **Logic**: 
  1. Fetch all assessments for class/subject (optionally filtered by date range)
  2. For each assessment, calculate class average
  3. Fetch all students enrolled in the class
  4. For each student, calculate student average and fetch individual marks
  5. Assemble read-only data structure

## Data Integrity Rules

### Referential Integrity
- Teacher foreign keys use `ON DELETE RESTRICT` for Phase 1 entities (lesson_plans, assessments)
- All other foreign keys use `ON DELETE CASCADE` for Phase 1 entities
- Phase 0 entities cascade to Phase 1 entities:
  - Delete Teacher → RESTRICTED by lesson_plans, assessments (must delete those first)
  - Delete Class → cascade to lesson_plans, assessments
  - Delete Subject → cascade to lesson_plans, assessments
  - Delete Student → cascade to assessment_marks
  - Delete Assessment → cascade to assessment_marks

### Validation Rules
- **Lesson Plans**: instructional_notes is nullable (supports empty drafts), status must be 'draft' or 'finalized'
- **Assessments**: No date constraints, maximum_marks is optional
- **Assessment Marks**:
  - Value must be >= 0
  - Value must be <= maximum_marks (if maximum_marks is defined)
  - Student must be enrolled in assessment's class
  - No duplicate (assessment_id, student_id) pairs

### Uniqueness Constraints
- Primary keys enforce uniqueness for all entity IDs
- `(assessment_id, student_id)` is unique in assessment_marks
- `(school_id, name)` is unique for grades and subjects
- `(school_id, date)` is unique for teaching_days and holidays

## Implementation Notes

- Use UUID for all entity IDs
- Store dates as ISO 8601 strings (YYYY-MM-DD)
- No caching or optimization
- No background recalculation of averages
- All aggregations computed on-demand
- No UI components
- No authentication or authorization
