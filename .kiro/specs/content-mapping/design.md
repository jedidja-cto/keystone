# Design Document: Content Mapping (Phase 3)

## Overview

This design implements Phase 3 of the Keystone project: optional content mapping. The system allows teachers to anchor their plans to physical or digital materials without assuming universal access. Phase 3 is strictly annotative—it references content but never drives planning, enforces completion, or assumes equity.

Implementation uses Python with SQLite for content mapping persistence. All content mapping is optional and teacher-controlled.

## Core Design Principles

1. **Optional, not required**: All content mapping is teacher-controlled
2. **Inequality-aware**: No assumption of universal textbook access
3. **Supportive, not authoritarian**: Materials inform, never drive planning
4. **No forced digital adoption**: Physical and digital treated equally
5. **No completion enforcement**: Page ranges are reference, not requirements
6. **Phase isolation**: Read-only access to Phase 0, 1, and 2 data

## Data Schema

### Phase 3 Entities (New - Persistent)

```sql
-- Textbooks (optional reference material)
CREATE TABLE textbooks (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    title TEXT NOT NULL,
    edition TEXT,
    publisher TEXT,
    isbn TEXT,
    publication_year INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
);

-- Content Mappings (topic → textbook content)
CREATE TABLE content_mappings (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    textbook_id TEXT NOT NULL,
    start_page INTEGER,
    end_page INTEGER,
    exercise_references TEXT,  -- Opaque teacher-authored string; system does not parse or interpret structure
    estimated_pages INTEGER,
    estimated_exercises INTEGER,
    estimated_time_minutes INTEGER,
    FOREIGN KEY (topic_id) REFERENCES curriculum_topics(id) ON DELETE CASCADE,
    FOREIGN KEY (textbook_id) REFERENCES textbooks(id) ON DELETE CASCADE
);

-- Lesson Content Alignments (lesson plan → content mapping)
CREATE TABLE lesson_content_alignments (
    lesson_plan_id TEXT NOT NULL,
    content_mapping_id TEXT NOT NULL,
    PRIMARY KEY (lesson_plan_id, content_mapping_id),
    FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (content_mapping_id) REFERENCES content_mappings(id) ON DELETE CASCADE
);
```

## Service Architecture

### Core Services

**TextbookService**
- `register_textbook(subject_id, title, **optional_fields)` → textbook_id
  - Optional registration of textbooks
  - No validation that textbooks are used
- `get_textbook(textbook_id)` → textbook_dict
- `list_textbooks(subject_id)` → list[textbook_dict]
- `update_textbook(textbook_id, **fields)` → success
- `delete_textbook(textbook_id)` → success
  - Deletion does not affect lesson plans (only removes content mappings)

**ContentMappingService**
- `create_content_mapping(topic_id, textbook_id, **optional_fields)` → mapping_id
  - All fields except topic_id and textbook_id are optional
  - Page ranges, exercises, workload estimates all optional
- `get_content_mapping(mapping_id)` → mapping_dict
- `list_content_mappings(topic_id=None, textbook_id=None)` → list[mapping_dict]
- `update_content_mapping(mapping_id, **fields)` → success
- `delete_content_mapping(mapping_id)` → success
  - Deletion does not affect lesson plans

**LessonContentAlignmentService**
- `align_lesson_to_content(lesson_plan_id, content_mapping_id)` → success
  - Optional association between lesson plan and content mapping
  - Lesson plans can exist without alignments
- `remove_alignment(lesson_plan_id, content_mapping_id)` → success
- `list_alignments_for_lesson(lesson_plan_id)` → list[content_mapping_dict]
- `list_lessons_for_content(content_mapping_id)` → list[lesson_plan_dict]

**WorkloadAggregationService**
- `calculate_workload_for_period(class_id, subject_id, start_date, end_date)` → workload_dict
  - Aggregates workload estimates from aligned content mappings
  - Returns: {
      "total_pages": int,
      "total_exercises": int,
      "total_time_minutes": int,
      "lesson_count": int,
      "aligned_lesson_count": int
    }
  - Only includes lessons with content alignments
  - All values are informational only (no enforcement)
- `calculate_workload_for_topic(topic_id)` → workload_dict
  - Aggregates workload from all content mappings for a topic
  - Returns: {
      "total_pages": int,
      "total_exercises": int,
      "total_time_minutes": int,
      "mapping_count": int
    }

## Relationships and Data Flow

### Content Mapping Hierarchy

```
Subject → Textbook (optional, 1..n)
                ↓
Curriculum_Topic → Content_Mapping (optional, 0..n)
                        ↓
                   Textbook (reference)
                        ↓
                   Page Range (optional)
                   Exercises (optional)
                   Workload Estimate (optional)
                        ↓
Lesson_Plan → Lesson_Content_Alignment (optional, 0..n)
                        ↓
                   Content_Mapping (reference)
```

### Content Mapping Flow

```
1. Teacher optionally registers textbook
   ↓
2. Teacher optionally maps curriculum topic to textbook content
   - Page range (optional)
   - Exercise references (optional)
   - Workload estimates (optional)
   ↓
3. Teacher optionally aligns lesson plan to content mapping
   ↓
4. System aggregates workload (informational only)
   - No enforcement
   - No errors if missing
   - No assumptions about student access
```

### Phase Isolation Boundaries

**Phase 3 MAY:**
- Read Phase 0 entities (subjects)
- Read Phase 2 entities (curriculum_topics)
- Read Phase 1 entities (lesson_plans)
- Create textbooks, content_mappings, lesson_content_alignments
- Delete textbooks and content_mappings (does not affect lesson plans)

**Phase 3 MUST NOT:**
- Modify Phase 0, 1, or 2 entities
- Require textbook selection for any operation
- Flag missing textbooks as errors
- Assume students have access to textbooks
- Generate student-facing content
- Enforce page completion
- Drive planning decisions

## Inequality-Aware Design

### No Assumptions About Access

Phase 3 is designed with explicit inequality awareness:

1. **Textbooks are optional**
   - Teachers can plan without registering any textbooks
   - No errors or warnings for missing textbooks
   - System functions fully without textbook data

2. **Content mappings are optional**
   - Topics can exist without content mappings
   - Lesson plans can exist without content alignments
   - No validation that content is mapped

3. **Workload aggregation excludes unmapped content**
   - Only counts lessons with explicit content alignments
   - Returns zero for unmapped content (not an error)
   - Clearly distinguishes aligned vs. unaligned lessons

4. **No student-facing assumptions**
   - Textbook references are teacher planning aids only
   - No tracking of student textbook access
   - No generation of student-facing content from mappings

### Physical and Digital Equality

```python
# Textbook entity treats physical and digital equally
textbook = {
    "id": "...",
    "title": "Algebra 1",
    "edition": "3rd Edition",
    "publisher": "Example Publisher",
    "isbn": "978-0-123456-78-9",  # Optional
    "publication_year": 2023       # Optional
}

# No "format" field - physical and digital are not distinguished
# Teachers use the same entity for both
```

## Workload Aggregation Logic

### Workload Calculation for Period

```python
def calculate_workload_for_period(class_id, subject_id, start_date, end_date):
    """
    Calculate aggregated workload for a planning period.
    
    Only includes lessons with explicit content alignments.
    All values are informational only (no enforcement).
    
    Returns:
        {
            "total_pages": int,
            "total_exercises": int,
            "total_time_minutes": int,
            "lesson_count": int,
            "aligned_lesson_count": int
        }
    """
    # Get all lesson plans in period (read-only)
    lesson_plans = query_lesson_plans(class_id, subject_id, start_date, end_date)
    
    total_pages = 0
    total_exercises = 0
    total_time_minutes = 0
    aligned_count = 0
    
    for lesson in lesson_plans:
        # Get content alignments for this lesson (read-only)
        alignments = query_lesson_content_alignments(lesson.id)
        
        if alignments:
            aligned_count += 1
            
            for alignment in alignments:
                # Get content mapping (read-only)
                mapping = query_content_mapping(alignment.content_mapping_id)
                
                # Aggregate workload estimates (all optional)
                total_pages += mapping.estimated_pages or 0
                total_exercises += mapping.estimated_exercises or 0
                total_time_minutes += mapping.estimated_time_minutes or 0
    
    return {
        "total_pages": total_pages,
        "total_exercises": total_exercises,
        "total_time_minutes": total_time_minutes,
        "lesson_count": len(lesson_plans),
        "aligned_lesson_count": aligned_count
    }
```

### Workload Calculation for Topic

```python
def calculate_workload_for_topic(topic_id):
    """
    Calculate aggregated workload for a curriculum topic.
    
    Sums workload from all content mappings for the topic.
    All values are informational only (no enforcement).
    
    Returns:
        {
            "total_pages": int,
            "total_exercises": int,
            "total_time_minutes": int,
            "mapping_count": int
        }
    """
    # Get all content mappings for topic (read-only)
    mappings = query_content_mappings_for_topic(topic_id)
    
    total_pages = 0
    total_exercises = 0
    total_time_minutes = 0
    
    for mapping in mappings:
        # Aggregate workload estimates (all optional)
        total_pages += mapping.estimated_pages or 0
        total_exercises += mapping.estimated_exercises or 0
        total_time_minutes += mapping.estimated_time_minutes or 0
    
    return {
        "total_pages": total_pages,
        "total_exercises": total_exercises,
        "total_time_minutes": total_time_minutes,
        "mapping_count": len(mappings)
    }
```

## Data Integrity Rules

### Referential Integrity

```sql
-- Textbooks reference Phase 0 subjects
textbooks.subject_id → subjects.id (CASCADE)

-- Content mappings reference Phase 2 topics and Phase 3 textbooks
content_mappings.topic_id → curriculum_topics.id (CASCADE)
content_mappings.textbook_id → textbooks.id (CASCADE)

-- Lesson content alignments reference Phase 1 lesson plans and Phase 3 content mappings
lesson_content_alignments.lesson_plan_id → lesson_plans.id (CASCADE)
lesson_content_alignments.content_mapping_id → content_mappings.id (CASCADE)
```

### Validation Rules

**Textbooks:**
- Title is required
- Edition, publisher, ISBN, publication year are optional
- No validation that textbooks are used
- No errors for unused textbooks

**Content Mappings:**
- topic_id and textbook_id are required
- All other fields are optional (page ranges, exercises, workload)
- No validation that page ranges are valid
- No validation that exercises exist
- No enforcement of workload estimates

**Lesson Content Alignments:**
- Optional association (lesson plans can exist without alignments)
- Multiple alignments per lesson plan allowed
- No validation that aligned content is appropriate
- Deletion of alignment does not affect lesson plan

### Uniqueness Constraints

- Primary keys enforce uniqueness for all entity IDs
- `(lesson_plan_id, content_mapping_id)` is unique in lesson_content_alignments
- No uniqueness constraint on content mappings (multiple mappings per topic allowed)

## Read-Only Access to Phase 0, 1, and 2

Phase 3 services read but never modify:

**Phase 0 Entities (Read-Only):**
- subjects (for textbook association)

**Phase 1 Entities (Read-Only):**
- lesson_plans (for content alignment)

**Phase 2 Entities (Read-Only):**
- curriculum_topics (for content mapping)

**Read-Only Query Examples:**

```python
# Read curriculum topics for content mapping
def get_topics_for_mapping(unit_id):
    """Read curriculum topics without modification."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, estimated_weeks
            FROM curriculum_topics
            WHERE unit_id = ?
            ORDER BY sequence_order, name
        """, (unit_id,))
        return [dict(row) for row in cursor.fetchall()]

# Read lesson plans for content alignment
def get_lessons_for_alignment(class_id, subject_id, start_date, end_date):
    """Read lesson plans without modification."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, topic, start_date, end_date, status
            FROM lesson_plans
            WHERE class_id = ? AND subject_id = ?
              AND start_date >= ? AND end_date <= ?
            ORDER BY start_date
        """, (class_id, subject_id, start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]
```

## Implementation Notes

- Use UUID for textbooks, content_mappings IDs
- All entity IDs are generated internally by the service layer; callers never provide IDs
- Store dates as ISO 8601 strings (YYYY-MM-DD)
- All workload estimates are optional integers
- Exercise references stored as text (comma-separated or JSON)
- No caching or optimization
- No background processing
- All aggregations computed on-demand
- Workload aggregates are informational only (no enforcement)

## Design Decisions

1. **Optional Everything**: Every aspect of Phase 3 is optional—textbooks, mappings, alignments, workload estimates
2. **No Validation**: No validation that textbooks exist, pages are valid, or exercises are real
3. **No Enforcement**: Workload aggregates are informational only, never enforced
4. **Physical = Digital**: No distinction between physical and digital textbooks
5. **Annotation, Not Mutation**: Content mapping annotates existing entities, never modifies them
6. **Deletion Safety**: Deleting textbooks or mappings does not affect lesson plans
7. **Inequality-First**: Design explicitly avoids assumptions about student access
8. **Teacher Authority**: All content mapping decisions are teacher-controlled

## Success Criteria Validation

✓ **Teachers can optionally reference textbooks and materials in their plans**
- `register_textbook()` allows optional textbook registration
- `create_content_mapping()` maps topics to textbook content
- `align_lesson_to_content()` associates lesson plans with content
- All operations are optional (no requirements)

✓ **Workload estimation helps teachers gauge realistic pacing**
- Content mappings include optional workload estimates
- `calculate_workload_for_period()` aggregates estimates
- `calculate_workload_for_topic()` shows topic-level workload
- All aggregates are informational only (no enforcement)

✓ **The system never assumes or enforces textbook access**
- No required textbook selection
- No errors for missing textbooks
- No validation that students have access
- Textbook references are teacher planning aids only
- No student-facing content generation
- Physical and digital treated equally

## Integration with Phase 0, 1, and 2

Phase 3 integrates cleanly with existing phases:

- **Reads** Phase 0 subjects for textbook association
- **Reads** Phase 2 curriculum topics for content mapping
- **Reads** Phase 1 lesson plans for content alignment
- **Never modifies** any existing phase data
- **Respects** all existing validation rules and constraints
- **Maintains** phase isolation boundaries

## Known Limitations (By Design)

1. No UI (command-line/API only)
2. No authentication or authorization
3. No caching or optimization
4. No background processing
5. No audit logging
6. No soft deletes
7. Single-database deployment only
8. No textbook content hosting
9. No student-facing features
10. No enforcement of any kind

These limitations are intentional for Phase 3. Future phases may address some as needed, but many (like no enforcement) are permanent design principles.
