# Keystone

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Status](https://img.shields.io/badge/status-active-success)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

A teacher-first operational platform designed to reduce administrative burden and give educators more time for what matters most: mentoring students.

## Purpose

Keystone helps teachers manage lesson planning, assessment logging, and reporting — automating the paperwork so they can focus on teaching. The system is built on the principle that saved time should be reinvested into human interaction, not more administration.

## Core Philosophy

- **Teacher-first UX, student-first outcomes** — The interface respects teachers' time and expertise while improving student support
- **Nothing is enforced; everything is suggested** — The system assists rather than dictates
- **Time saved is time reinvested** — Automation serves human connection
- **Raw data stays internal** — External outputs are interpreted summaries, not raw scores
- **Adoption over complexity** — Simplicity and trust drive usage

## Intended Users

- **Primary users:** Teachers
- **Secondary beneficiaries:** Students
- **Tertiary recipients:** Parents (via reports only, no accounts initially)

## What Keystone Is

A teacher operational platform that:
- Reduces administrative workload
- Improves lesson planning efficiency
- Automates assessment aggregation
- Generates readable, trustworthy reports
- Respects teacher autonomy and professional judgment

## What Keystone Is NOT

- Not a learning platform (e.g., Google Classroom)
- Not a student social system
- Not an AI grading tool
- Not a parent portal (initially)
- Not a rigid curriculum enforcer

## Functional Areas

### Lesson Planning
Calendar-aware planning that aligns with curriculum standards. Draft-based and editable — premeditated but never enforced.

### Assessment Logging
Quantitative score tracking with automatic aggregation and performance trend analysis.

### Qualitative Observations
Optional, time-based observations with structured and free-text formats. Internal only — never exposed externally.

### Aggregation & Reporting
Teacher insights, student summaries, and parent-readable reports that interpret data rather than expose raw scores.

### Calendar Intelligence
Academic term tracking, holidays, teaching days, and exam periods.

### Optional Content Mapping
Textbook references, page ranges, and workload estimation — never assumed, always optional.

## Development Approach

Keystone is being built in phases, with each phase fully defined before implementation begins. Development follows a structured, incremental approach where features are specified, designed, and implemented systematically.

## Success Criteria

- Teachers feel respected, not evaluated
- Administrative workload decreases measurably
- Reports are accurate, readable, and trusted
- The system scales by trust, not force

---

## Phase 1 Implementation Status: ✓ COMPLETE

Phase 0 (Foundational Data) and Phase 1 (Teacher Core Operations) have been implemented.

## Phase 2 Implementation Status: ✓ COMPLETE

Phase 2 (Premeditated Planning Engine) has been implemented.

## Phase 3 Implementation Status: ✓ COMPLETE

Phase 3 (Optional Content Mapping) has been implemented.

## Phase 4 Implementation Status: ✓ COMPLETE

Phase 4 (Qualitative Observations) has been implemented.

## Phase 5 Implementation Status: ✓ COMPLETE

Phase 5 (Aggregation & Reporting) has been implemented.

## Phase 6 Implementation Status: ✓ COMPLETE

Phase 6 (Operational Trial & Professionalization) has been implemented.

### Phase 1 Success Criteria Met

✓ **Teachers can plan lessons without changing how they think**
- Flexible date associations (specific day, range, or unscheduled)
- Free-text instructional notes
- No curriculum validation
- Edit at any time

✓ **Teachers can log marks faster than using spreadsheets**
- Simple mark entry with automatic validation
- Prevents common errors (exceeding max, wrong class)
- Update or delete marks easily

✓ **System provides immediate, understandable summaries**
- Class averages calculated on-demand
- Student averages across assessments
- Export summaries with all relevant metadata

### Phase 2 Success Criteria Met

✓ **Teachers can see a clear, realistic pacing plan before a term starts**
- Draft plans show weekly breakdown with dates
- Planning window calculated from real teaching days
- Risk signals flag potential issues (informational only)

✓ **Planning suggestions respect calendar constraints and curriculum scope**
- Holidays and exam periods excluded from planning
- Topics distributed across available weeks
- Compression risks flagged when scope exceeds time

✓ **Teachers remain fully in control of what becomes an actual lesson plan**
- Draft plans are in-memory only (non-persistent)
- Explicit confirmation required before creating lesson plans
- Lesson plans created as drafts (teacher can edit)
- No instructional content generated automatically

### Phase 3 Success Criteria Met

✓ **Teachers can optionally reference textbooks and materials in their plans**
- Textbook registration and management
- Mapping topics to specific sections/page ranges
- Alignment between lesson plans and content mappings

✓ **Workload estimation helps teachers gauge realistic pacing**
- Estimated pages, exercises, and time per mapping
- Aggregated workload summaries for planning periods

✓ **The system never assumes or enforces textbook access**
- All textbook data is optional and teacher-controlled
- System functions fully without any textbook references
- No student-facing enforcement

## Requirements

- Python 3.8+
- No external dependencies (uses standard library sqlite3)

## Quick Start

```bash
# Run Phase 1 example
python example.py

# Run Phase 2 example
python example_phase2.py

# Run Phase 3 example
python example_phase3.py
```

**Phase 1 example** demonstrates:
- Creating foundational entities (school, teacher, students, class, subject)
- Creating and updating lesson plans
- Creating assessments with marks
- Calculating class and student averages
- Generating export summaries

**Phase 2 example** demonstrates:
- Loading curriculum structure (units and topics)
- Calculating planning windows (teaching days, holidays, exam periods)
- Generating draft planning proposals
- Detecting risk signals (compression, gaps, overload)
- Accepting drafts with explicit confirmation
- Creating lesson plans from approved drafts

## Architecture

The system uses Python with SQLite for data persistence. No UI, no optimization, no future-proofing—just the smallest correct system that satisfies the requirements.

### Services

- **DatabaseService**: Manages SQLite connection and schema
- **LessonPlanService**: CRUD operations for lesson plans
- **AssessmentService**: CRUD operations for assessments
- **AssessmentMarkService**: CRUD operations for assessment marks with validation
- **AggregationService**: Calculates class/student averages and generates export summaries
- **CurriculumService**: Read-only access to curriculum structure (Phase 2)
- **CalendarService**: Calendar-aware planning calculations (Phase 2)
- **PacingCalculationService**: Pacing suggestions and risk detection (Phase 2)
- **DraftPlanningService**: Draft plan generation and management (Phase 2)
- **TextbookService**: Optional textbook registration (Phase 3)
- **ContentMappingService**: Topic-to-content mapping (Phase 3)
- **LessonContentAlignmentService**: Alignment between plans and content (Phase 3)
- **WorkloadAggregationService**: Aggregated workload calculation (Phase 3)
- **QualitativeObservationService**: Manages student observations (Phase 4)
- **ReportGenerationService**: Unified parent-ready report generation (Phase 5)
- **ImportService**: Bulk CSV data management (Phase 6)
- **KeystoneCLI**: Unified command-line interface (Phase 6)

### Data Schema

**Phase 0 Entities (Foundation)**
- Schools, Teachers, Students, Classes, Subjects, Grades
- Academic Calendar (Terms, Teaching Days, Holidays, Exam Periods)
- Relationships: Student-Class enrollment, Teacher-Class assignment, Class-Subject mapping

**Phase 1 Entities (New)**
- **Lesson Plans**: Teacher-created instructional plans with flexible scheduling
- **Assessments**: Evaluation instruments with optional maximum marks
- **Assessment Marks**: Student performance records with validation

**Phase 3 Entities (New)**
- **Textbooks**: Optional reference materials mapping to subjects
- **Content Mappings**: Linkage between curriculum topics and textbook sections
- **Lesson Content Alignments**: Association between specific lessons and mappings

**Phase 4 Entities (New)**
- **Qualitative Observations**: Time-based student observations with categorical data

**Phase 5 Logic**
- **Report Synthesis**: On-demand generation of parent-readable summaries

## Usage Example

```python
from src import (
    DatabaseService,
    LessonPlanService,
    AssessmentService,
    AssessmentMarkService,
    AggregationService
)

# Initialize services
db = DatabaseService("myschool.db")
lesson_plan_service = LessonPlanService(db)
assessment_service = AssessmentService(db)
mark_service = AssessmentMarkService(db)
aggregation_service = AggregationService(db)

# Create a lesson plan
lesson_plan_id = lesson_plan_service.create_lesson_plan(
    teacher_id="teacher-uuid",
    class_id="class-uuid",
    subject_id="subject-uuid",
    status="draft",
    instructional_notes="Introduction to algebra",
    topic="Algebra Basics"
)

# Create an assessment
assessment_id = assessment_service.create_assessment(
    teacher_id="teacher-uuid",
    class_id="class-uuid",
    subject_id="subject-uuid",
    date="2024-01-20",
    name="Algebra Quiz",
    maximum_marks=100.0
)

# Enter marks
mark_id = mark_service.create_mark(
    assessment_id=assessment_id,
    student_id="student-uuid",
    value=85.0
)

# Calculate class average
class_avg = aggregation_service.calculate_class_average(assessment_id)

# Calculate student average
student_avg = aggregation_service.calculate_student_average(
    student_id="student-uuid",
    class_id="class-uuid",
    subject_id="subject-uuid"
)

# Generate export summary
summary = aggregation_service.generate_export_summary(
    class_id="class-uuid",
    subject_id="subject-uuid",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── database.py              # Database service and schema
│   ├── lesson_plan_service.py   # Lesson plan CRUD
│   ├── assessment_service.py    # Assessment CRUD
│   ├── assessment_mark_service.py  # Mark CRUD with validation
│   └── aggregation_service.py   # Averages and export summaries
├── .kiro/
│   └── specs/
│       ├── foundational-data/
│       │   └── requirements.md  # Phase 0 requirements
│       └── teacher-core-operations/
│           ├── requirements.md  # Phase 1 requirements
│           └── design.md        # Phase 1 design
├── example.py                   # Example usage
├── requirements.txt             # Dependencies (none)
└── README.md                    # This file
```

## Validation Rules

### Lesson Plans
- `instructional_notes` is nullable (supports empty drafts)
- `status` must be 'draft' or 'finalized'
- No content validation or curriculum constraints

### Assessments
- No date constraints
- `maximum_marks` is optional

### Assessment Marks
- Value must be >= 0
- Value must be <= maximum_marks (if maximum_marks is defined)
- Student must be enrolled in assessment's class
- No duplicate (assessment_id, student_id) pairs

## Data Integrity

- Foreign key constraints with appropriate CASCADE/RESTRICT behavior
- Teacher deletion is RESTRICTED (must delete lesson plans/assessments first)
- Uniqueness constraints on identifiers and key combinations
- Date validation for terms and exam periods

## Design Decisions

1. **No UI**: Focus on correct data operations only
2. **No Optimization**: On-demand calculation of averages (no caching)
3. **No Future-Proofing**: Implements exactly what Phase 1 requires
4. **SQLite**: Simple, embedded database with full SQL support
5. **UUID Identifiers**: Globally unique IDs for all entities
6. **ISO 8601 Dates**: Standard date format (YYYY-MM-DD)
