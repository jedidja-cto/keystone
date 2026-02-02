# Design Document: Premeditated Planning Engine (Phase 2)

## Overview

This design implements Phase 2 of the Keystone project: the Premeditated Planning Engine. The system provides assistive, calendar-aware planning suggestions that teachers can accept, modify, or discard. All outputs are proposals—never automatic actions. Phase 2 reads Phase 0 and Phase 1 data but never mutates it directly.

Implementation uses Python with SQLite for curriculum data persistence. Draft plans are non-persistent in-memory structures until explicitly accepted by teachers.

## Core Design Principles

1. **Assistive, not authoritarian**: System suggests; teacher decides
2. **No silent mutation**: No lesson plans created without explicit confirmation
3. **Calendar-aware by default**: All suggestions account for real teaching time
4. **Curriculum-respecting, not enforcing**: Curricula inform structure, not pedagogy
5. **Phase isolation**: Read-only access to Phase 0 and Phase 1 data

## Data Schema

### Phase 2 Entities (New - Persistent)

```sql
-- Curriculum Units
CREATE TABLE curriculum_units (
    id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    grade_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    sequence_order INTEGER,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(school_id, grade_id, subject_id, name)
);

-- Curriculum Topics
CREATE TABLE curriculum_topics (
    id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    sequence_order INTEGER,
    estimated_weeks INTEGER,
    FOREIGN KEY (unit_id) REFERENCES curriculum_units(id) ON DELETE CASCADE,
    UNIQUE(unit_id, name)
);
```

### Phase 2 Entities (Non-Persistent - In-Memory Only)

Draft plans are **never** stored in the database. They exist only as in-memory data structures during a planning session.

```python
# Draft Plan Structure (In-Memory Only)
DraftPlan = {
    "session_id": str,  # Unique session identifier
    "teacher_id": str,
    "class_id": str,
    "subject_id": str,
    "planning_window": {
        "start_date": str,  # ISO 8601
        "end_date": str,    # ISO 8601
        "available_teaching_days": int,
        "lost_days": [
            {
                "date": str,
                "reason": str  # "holiday", "exam_period", "non_teaching"
            }
        ]
    },
    "pacing_suggestions": [
        {
            "week_number": int,
            "week_start_date": str,
            "week_end_date": str,
            "unit_id": str,
            "unit_name": str,
            "topics": [
                {
                    "topic_id": str,
                    "topic_name": str,
                    "estimated_weeks": int
                }
            ]
        }
    ],
    "risk_signals": [
        {
            "type": str,  # "compression", "gap", "overload"
            "severity": str,  # "info", "warning", "critical"
            "message": str,
            "affected_weeks": [int]
        }
    ],
    "existing_plans_context": [
        {
            "lesson_plan_id": str,
            "date": str,
            "topic": str
        }
    ],
    "existing_assessments_context": [
        {
            "assessment_id": str,
            "date": str,
            "name": str
        }
    ],
    "created_at": str,  # ISO 8601 timestamp
    "modified_at": str  # ISO 8601 timestamp
}
```

## Service Architecture

### Core Services

**CurriculumService**
- `load_curriculum(school_id, grade_id, subject_id, curriculum_data)` → success
  - Import curriculum structure from official or national standards
  - Create curriculum_units and curriculum_topics records
  - Used for initial curriculum ingestion only
- `get_unit(unit_id)` → unit_dict
- `list_units(school_id, grade_id, subject_id)` → list[unit_dict]
- `get_topic(topic_id)` → topic_dict
- `list_topics(unit_id)` → list[topic_dict]
- `get_curriculum_structure(school_id, grade_id, subject_id)` → curriculum_hierarchy_dict
  - Returns complete hierarchy: units with nested topics
  - Read-only access to curriculum reference material

**CalendarService**
- `calculate_teaching_days(school_id, start_date, end_date)` → list[date]
  - Query teaching_days table for dates in range
  - Exclude dates in holidays table
  - Exclude dates within exam_periods
  - Return sorted list of available teaching dates
- `identify_lost_days(school_id, start_date, end_date)` → list[lost_day_dict]
  - Query holidays and exam_periods
  - Return list with date and reason for each lost day
- `get_planning_window(school_id, start_date, end_date)` → planning_window_dict
  - Calculate available teaching days
  - Identify lost days
  - Return structured planning window data

**DraftPlanningService**
- `generate_draft_plan(teacher_id, class_id, subject_id, start_date, end_date)` → draft_plan_dict
  - Read curriculum structure (units and topics)
  - Calculate planning window via CalendarService
  - Read existing lesson plans (read-only)
  - Read existing assessments (read-only)
  - Generate pacing suggestions
  - Identify risk signals
  - Return in-memory draft plan structure
- `modify_draft_plan(session_id, modifications)` → draft_plan_dict
  - Apply teacher modifications to in-memory draft
  - Recalculate pacing if needed
  - Update risk signals
  - Return updated draft plan
- `reorder_topics(session_id, new_order)` → draft_plan_dict
  - Reorder topics within draft plan
  - Recalculate pacing
  - Return updated draft plan
- `discard_draft_plan(session_id)` → success
  - Remove draft from memory
  - No database operations
- `accept_draft_plan(session_id, confirmation_token)` → list[lesson_plan_id]
  - Require explicit confirmation token
  - Convert draft plan to Lesson_Plan records via Phase 1 LessonPlanService
  - Return list of created lesson plan IDs
  - Remove draft from memory

**PacingCalculationService**
- `calculate_pacing(curriculum_scope, available_weeks)` → pacing_suggestion_list
  - Distribute topics across available weeks
  - Aim for balanced weekly load
  - Return weekly breakdown
- `detect_compression_risk(curriculum_scope, available_weeks)` → risk_signal_list
  - Flag when curriculum scope exceeds available time
  - Identify overloaded weeks
  - Return informational risk signals (no enforcement)
- `detect_gaps(existing_plans, planning_window)` → risk_signal_list
  - Identify weeks with no planned content
  - Return informational gap signals (no enforcement)

## Relationships and Data Flow

### Curriculum Structure Hierarchy

```
School → Grade → Subject
                    ↓
            Curriculum_Unit (1..n)
                    ↓
            Curriculum_Topic (1..n)
```

### Draft Plan Generation Flow

```
1. Teacher requests draft plan
   ↓
2. DraftPlanningService reads:
   - Curriculum structure (curriculum_units, curriculum_topics)
   - Calendar data (teaching_days, holidays, exam_periods) [READ-ONLY]
   - Existing lesson plans (lesson_plans) [READ-ONLY]
   - Existing assessments (assessments) [READ-ONLY]
   ↓
3. CalendarService calculates planning window
   ↓
4. PacingCalculationService generates pacing suggestions
   ↓
5. Risk signals identified (compression, gaps, overload)
   ↓
6. Draft plan returned as in-memory structure
   ↓
7. Teacher reviews, modifies, reorders, or discards
   ↓
8. If accepted with confirmation:
   - DraftPlanningService calls Phase 1 LessonPlanService
   - Lesson_Plan records created
   - Draft removed from memory
```

### Phase Isolation Boundaries

**Phase 2 MAY:**
- Read Phase 0 entities (schools, teachers, classes, subjects, grades, calendar)
- Read Phase 1 entities (lesson_plans, assessments)
- Create curriculum_units and curriculum_topics
- Generate in-memory draft plans
- Call Phase 1 LessonPlanService.create_lesson_plan() when teacher accepts draft

**Phase 2 MUST NOT:**
- Modify Phase 0 entities
- Modify Phase 1 entities (lesson_plans, assessments)
- Automatically create lesson plans without explicit teacher confirmation
- Persist draft plans to database
- Enforce curriculum completion
- Mandate teaching order

## Calendar-Aware Pacing Logic

### Planning Window Calculation

```python
def calculate_planning_window(school_id, start_date, end_date):
    """
    Calculate available teaching time within date range.
    
    Note: Week calculation uses heuristic default (5 teaching days = 1 week).
    This is a configurable constant, not an enforced policy.
    
    Returns:
        {
            "start_date": str,
            "end_date": str,
            "available_teaching_days": int,
            "available_weeks": int,
            "lost_days": [
                {"date": str, "reason": str}
            ]
        }
    """
    # Query teaching_days in range
    teaching_days = query_teaching_days(school_id, start_date, end_date)
    
    # Query holidays in range
    holidays = query_holidays(school_id, start_date, end_date)
    
    # Query exam_periods overlapping range
    exam_periods = query_exam_periods(school_id, start_date, end_date)
    
    # Calculate available days
    available_days = teaching_days - holidays - exam_period_days
    
    # Convert to weeks (heuristic: 5 teaching days = 1 week)
    DAYS_PER_WEEK = 5  # Configurable constant
    available_weeks = available_days // DAYS_PER_WEEK
    
    # Identify lost days with reasons
    lost_days = []
    for holiday in holidays:
        lost_days.append({"date": holiday.date, "reason": "holiday"})
    for exam_date in exam_period_days:
        lost_days.append({"date": exam_date, "reason": "exam_period"})
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "available_teaching_days": len(available_days),
        "available_weeks": available_weeks,
        "lost_days": lost_days
    }
```

### Pacing Distribution Algorithm

```python
def calculate_pacing(units_with_topics, available_weeks):
    """
    Distribute curriculum topics across available weeks.
    
    Algorithm (heuristic defaults, not enforced limits):
    1. Sum total estimated weeks from all topics
    2. If total > available_weeks, flag compression risk
    3. Distribute topics sequentially across weeks
    4. Heuristic: Prefer max 2 topics per week (configurable, not enforced)
    5. Return weekly breakdown
    
    Note: These are internal heuristics, not policy guarantees.
    Teachers may override any pacing suggestion.
    
    Returns:
        [
            {
                "week_number": int,
                "week_start_date": str,
                "week_end_date": str,
                "unit_id": str,
                "unit_name": str,
                "topics": [topic_dict]
            }
        ]
    """
    total_estimated_weeks = sum(topic.estimated_weeks for topic in all_topics)
    
    pacing_suggestions = []
    current_week = 1
    
    for unit in units_with_topics:
        for topic in unit.topics:
            # Assign topic to current week
            pacing_suggestions.append({
                "week_number": current_week,
                "unit_id": unit.id,
                "unit_name": unit.name,
                "topics": [topic]
            })
            
            # Advance weeks based on estimated duration
            current_week += topic.estimated_weeks or 1
    
    return pacing_suggestions
```

### Risk Signal Detection

```python
def detect_risks(pacing_suggestions, available_weeks, existing_plans):
    """
    Identify planning risks (informational only, no enforcement).
    
    Risk Types:
    - compression: Curriculum scope exceeds available time
    - overload: Too many topics in a single week
    - gap: Weeks with no planned content
    
    Returns:
        [
            {
                "type": str,
                "severity": str,
                "message": str,
                "affected_weeks": [int]
            }
        ]
    """
    risks = []
    
    # Compression risk
    total_weeks_needed = max(ps["week_number"] for ps in pacing_suggestions)
    if total_weeks_needed > available_weeks:
        risks.append({
            "type": "compression",
            "severity": "warning",
            "message": f"Curriculum requires {total_weeks_needed} weeks but only {available_weeks} available",
            "affected_weeks": list(range(available_weeks + 1, total_weeks_needed + 1))
        })
    
    # Overload risk (heuristic: flag if > 2 topics per week)
    topics_per_week = {}
    for ps in pacing_suggestions:
        week = ps["week_number"]
        topics_per_week[week] = topics_per_week.get(week, 0) + len(ps["topics"])
    
    MAX_TOPICS_PER_WEEK = 2  # Configurable heuristic, not enforced limit
    for week, count in topics_per_week.items():
        if count > MAX_TOPICS_PER_WEEK:
            risks.append({
                "type": "overload",
                "severity": "info",
                "message": f"Week {week} has {count} topics (consider spreading)",
                "affected_weeks": [week]
            })
    
    # Gap detection
    planned_weeks = set(ps["week_number"] for ps in pacing_suggestions)
    all_weeks = set(range(1, available_weeks + 1))
    gap_weeks = all_weeks - planned_weeks
    
    if gap_weeks:
        risks.append({
            "type": "gap",
            "severity": "info",
            "message": f"Weeks {sorted(gap_weeks)} have no planned content",
            "affected_weeks": sorted(gap_weeks)
        })
    
    return risks
```

## Teacher Control and Confirmation

### Draft Modification Operations

Teachers can modify drafts through these operations:

1. **Reorder topics**: Change sequence without changing curriculum structure
2. **Modify pacing**: Adjust weeks allocated to topics
3. **Include/exclude topics**: Include or exclude topics from the draft plan (without modifying curriculum structure)
4. **Adjust dates**: Change planning window

All modifications update the in-memory draft only. No database writes occur. Teachers cannot add new topics or delete curriculum topics—they can only choose which existing curriculum topics to include in their draft plan.

### Explicit Confirmation Requirement

When a teacher accepts a draft plan, the system MUST:

1. Generate a unique confirmation token
2. Present summary of lesson plans to be created
3. Require teacher to provide confirmation token
4. Only then create Lesson_Plan records via Phase 1 LessonPlanService

**Important clarifications about accepted drafts:**
- Lesson plans are created with `status="draft"` (not finalized)
- No instructional content is generated (only topic names and dates)
- Dates are coarse (week-level ranges, not day-locked)
- Teachers are expected to review and edit each lesson plan individually after creation
- This is a bulk scaffolding operation, not a final planning step

1. Generate a unique confirmation token
2. Present summary of lesson plans to be created
3. Require teacher to provide confirmation token
4. Only then create Lesson_Plan records via Phase 1 LessonPlanService

```python
def accept_draft_plan(session_id, confirmation_token):
    """
    Convert draft plan to persisted lesson plans.
    
    Requires explicit confirmation token to prevent accidental creation.
    """
    # Validate confirmation token
    if not validate_confirmation_token(session_id, confirmation_token):
        raise ValueError("Invalid confirmation token")
    
    # Retrieve draft from memory
    draft = get_draft_from_memory(session_id)
    
    # Create lesson plans via Phase 1 service
    lesson_plan_ids = []
    for week in draft["pacing_suggestions"]:
        for topic in week["topics"]:
            # Call Phase 1 LessonPlanService
            lp_id = lesson_plan_service.create_lesson_plan(
                teacher_id=draft["teacher_id"],
                class_id=draft["class_id"],
                subject_id=draft["subject_id"],
                status="draft",
                instructional_notes=None,
                topic=topic["topic_name"],
                start_date=week["week_start_date"],
                end_date=week["week_end_date"]
            )
            lesson_plan_ids.append(lp_id)
    
    # Remove draft from memory
    remove_draft_from_memory(session_id)
    
    return lesson_plan_ids
```

## Data Integrity Rules

### Referential Integrity

```sql
-- Curriculum units reference Phase 0 entities
curriculum_units.school_id → schools.id (CASCADE)
curriculum_units.grade_id → grades.id (CASCADE)
curriculum_units.subject_id → subjects.id (CASCADE)

-- Curriculum topics reference curriculum units
curriculum_topics.unit_id → curriculum_units.id (CASCADE)
```

### Validation Rules

**Curriculum Units:**
- Unique (school_id, grade_id, subject_id, name)
- sequence_order is optional

**Curriculum Topics:**
- Unique (unit_id, name)
- sequence_order is optional
- estimated_weeks is optional (default: 1)

**Draft Plans:**
- Never persisted to database
- Stored in memory only during planning session
- Automatically discarded after timeout or explicit discard
- No referential integrity constraints (not in database)

### Uniqueness Constraints

- `(school_id, grade_id, subject_id, name)` is unique for curriculum_units
- `(unit_id, name)` is unique for curriculum_topics

## Read-Only Access to Phase 0 and Phase 1

Phase 2 services read but never modify:

**Phase 0 Entities (Read-Only):**
- schools, grades, subjects, classes, teachers
- teaching_days, holidays, exam_periods, terms

**Phase 1 Entities (Read-Only):**
- lesson_plans (for contextual awareness)
- assessments (for timing constraints)

**Read-Only Query Examples:**

```python
# Read existing lesson plans for context
def get_existing_plans_context(class_id, subject_id, start_date, end_date):
    """Read existing lesson plans without modification."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, start_date, end_date, topic
            FROM lesson_plans
            WHERE class_id = ? AND subject_id = ?
              AND start_date >= ? AND end_date <= ?
        """, (class_id, subject_id, start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]

# Read existing assessments for context
def get_existing_assessments_context(class_id, subject_id, start_date, end_date):
    """Read existing assessments without modification."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, name
            FROM assessments
            WHERE class_id = ? AND subject_id = ?
              AND date >= ? AND date <= ?
        """, (class_id, subject_id, start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]
```

## Implementation Notes

- Use UUID for curriculum_units and curriculum_topics IDs
- Use UUID for draft plan session_ids
- Store dates as ISO 8601 strings (YYYY-MM-DD)
- Draft plans stored in memory (Python dict) with session timeout
- No caching or optimization
- No background processing
- All pacing calculations performed on-demand
- Risk signals are informational only (no enforcement)
- Teacher confirmation required before any lesson plan creation

## Design Decisions

1. **In-Memory Drafts**: Draft plans never touch the database, ensuring no accidental persistence
2. **Explicit Confirmation**: Confirmation token prevents accidental lesson plan creation
3. **Read-Only Phase Isolation**: Phase 2 cannot corrupt Phase 0 or Phase 1 data
4. **Informational Risk Signals**: System flags issues but never enforces solutions
5. **Teacher Authority**: All decisions require explicit teacher action
6. **No AI Content Generation**: System suggests structure and pacing, not lesson content
7. **Calendar-First**: All suggestions start with available teaching time, not curriculum scope

## Success Criteria Validation

✓ **Teachers can see a clear, realistic pacing plan before a term starts**
- `generate_draft_plan()` produces weekly breakdown
- Planning window calculated from real teaching days
- Pacing suggestions distributed across available weeks

✓ **Planning suggestions respect calendar constraints and curriculum scope**
- CalendarService excludes holidays, exams, non-teaching days
- PacingCalculationService distributes topics across available time
- Risk signals flag compression when scope exceeds time

✓ **Teachers remain fully in control of what becomes an actual lesson plan**
- Draft plans are in-memory only (non-persistent)
- Teachers can modify, reorder, or discard drafts
- Explicit confirmation required before creating lesson plans
- No automatic lesson plan creation
