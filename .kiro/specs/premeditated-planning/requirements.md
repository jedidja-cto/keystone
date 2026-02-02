# Requirements Document: Premeditated Planning Engine (Phase 2)

## Introduction

Phase 2 introduces the Premeditated Planning Engine, an assistive system that helps teachers plan ahead of time by reasoning over the academic calendar and curriculum structure. The system proposes draft planning suggestions that teachers may accept, modify, reorder, or discard.

Phase 2 does not create lesson plans automatically and does not override teacher intent. All outputs are proposals, never enforced actions.

**Success Criteria:** Phase 2 is successful if:
1. Teachers can see a clear, realistic pacing plan before a term starts
2. Planning suggestions respect calendar constraints and curriculum scope
3. Teachers remain fully in control of what becomes an actual lesson plan

## Core Principles (Non-Negotiable)

- **Assistive, not authoritarian** — The system suggests; the teacher decides.
- **No silent mutation** — No lesson plans are created without explicit teacher confirmation.
- **Calendar-aware by default** — All planning suggestions account for real teaching time.
- **Curriculum-respecting, not curriculum-enforcing** — Official curricula inform structure, not pedagogy.
- **Phase isolation** — Phase 2 may read Phase 0 and Phase 1 data but must not mutate them directly.

## Glossary

- **Planning_Window**: A date range representing available teaching days for instruction
- **Curriculum_Structure**: A hierarchical definition of Subject → Units → Topics
- **Draft_Plan**: A system-generated proposal that has not been persisted as lesson plans
- **Pacing_Suggestion**: A proposed distribution of curriculum topics across time
- **Lost_Day**: A teaching day unavailable due to holidays, exams, or closures
- **Accepted_Draft**: A teacher-approved draft that may be converted into lesson plans
- **Unit**: A major division of curriculum content within a subject
- **Topic**: A specific learning objective or content area within a unit

## Scope of Phase 2

### Included
- Calendar-aware pacing calculations
- Curriculum structure modeling
- Draft planning proposals
- Teacher-controlled acceptance and modification
- Read-only use of Phase 1 lesson and assessment data

### Explicitly Excluded
- Automatic lesson plan creation
- AI grading or evaluation
- Student-facing features
- Curriculum editing or authoring
- Enforcement of completion targets

## Requirements

### Requirement 1: Curriculum Hierarchy Definition

**User Story:** As a teacher, I want the system to understand the structure of my subject curriculum, so that planning suggestions align with official learning expectations.

#### Acceptance Criteria

1. THE System SHALL support a curriculum hierarchy consisting of:
   - Subject
   - Unit
   - Topic
2. THE System SHALL associate curriculum structures with a specific Grade and Subject
3. THE System SHALL allow curriculum data to be sourced from official or national standards
4. THE System SHALL treat curriculum data as reference material, not enforcement rules
5. THE System SHALL NOT mandate the order in which units or topics are taught

### Requirement 2: Teaching Time Awareness

**User Story:** As a teacher, I want planning suggestions to reflect real available teaching time, so that plans are achievable.

#### Acceptance Criteria

1. THE System SHALL calculate available teaching days within a selected date range
2. THE System SHALL exclude holidays, exam periods, and non-teaching days
3. THE System SHALL identify lost teaching days within a term
4. THE System SHALL derive a planning window based on remaining teaching days
5. THE System SHALL recalculate planning windows when calendar data changes

### Requirement 3: Pacing Window Calculation

**User Story:** As a teacher, I want the system to suggest realistic pacing, so that curriculum content fits within the term.

#### Acceptance Criteria

1. THE System SHALL calculate pacing suggestions based on:
   - Available teaching days
   - Curriculum scope (units and topics)
2. THE System SHALL distribute topics across weeks, not individual days
3. THE System SHALL avoid overloading any single week
4. THE System SHALL flag when curriculum scope exceeds available time
5. THE System SHALL NOT automatically adjust pacing without teacher input

### Requirement 4: Draft Plan Generation

**User Story:** As a teacher, I want the system to propose draft plans, so that I can start planning faster.

#### Acceptance Criteria

1. THE System SHALL generate draft planning proposals for a selected Class and Subject
2. THE System SHALL present weekly topic breakdowns
3. THE System SHALL include suggested pacing per unit or topic
4. THE System SHALL generate drafts without creating Lesson_Plan records
5. THE System SHALL treat all drafts as temporary and editable

### Requirement 5: Teacher Control Over Drafts

**User Story:** As a teacher, I want full control over planning drafts, so that the system works for me.

#### Acceptance Criteria

1. THE System SHALL allow teachers to accept draft proposals
2. THE System SHALL allow teachers to modify draft proposals
3. THE System SHALL allow teachers to reorder units or topics
4. THE System SHALL allow teachers to discard drafts entirely
5. WHEN a teacher accepts a draft, THE System SHALL require explicit confirmation before creating Lesson_Plan records

### Requirement 6: Read-Only Access to Existing Plans and Assessments

**User Story:** As a teacher, I want planning suggestions to reflect what I've already done, without altering existing data.

#### Acceptance Criteria

1. THE System SHALL read existing Lesson_Plans for contextual awareness
2. THE System SHALL read existing Assessments to understand timing constraints
3. THE System SHALL NOT modify existing Lesson_Plans or Assessments
4. THE System SHALL adjust draft proposals based on completed or planned work
5. THE System SHALL surface gaps or compression risks without enforcing changes

### Requirement 7: Non-Destructive Behavior

**User Story:** As a system owner, I want to ensure Phase 2 cannot damage existing data.

#### Acceptance Criteria

1. THE System SHALL NOT mutate Phase 0 or Phase 1 records directly
2. THE System SHALL treat draft proposals as separate, non-persistent entities
3. THE System SHALL require explicit teacher action to persist any planning data
4. THE System SHALL maintain referential integrity at all times

## Assumptions

- Curriculum data may vary by region and grade
- Teachers may choose non-linear teaching orders
- Not all curriculum topics must be completed
- Planning suggestions may be imperfect and are allowed to be overridden
- Teachers remain the final authority on planning decisions

## Out of Scope (Phase 2)

- Automated curriculum completion tracking
- Performance prediction
- AI-generated lesson content
- Student analytics
- Parent-facing outputs

---

**End of Phase 2 Requirements**

This document defines what Phase 2 must do, what it must never do, and where authority lies. Once approved, these requirements should be frozen before design or implementation begins.
