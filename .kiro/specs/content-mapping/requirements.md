# Requirements Document: Content Mapping (Phase 3)

## Introduction

Phase 3 introduces optional content mapping, allowing teachers to anchor their plans to physical or digital materials without assuming universal access. This phase provides a lens for referencing textbooks, page ranges, and workload estimates—never enforcing completion or assuming equity that doesn't exist.

Phase 3 does not drive planning, does not enforce pacing, and does not assume all students have access to materials. All content mapping is optional and teacher-controlled.

**Success Criteria:** Phase 3 is successful if:
1. Teachers can optionally reference textbooks and materials in their plans
2. Workload estimation helps teachers gauge realistic pacing
3. The system never assumes or enforces textbook access

## Core Principles (Non-Negotiable)

- **Optional, not required** — All content mapping is teacher-controlled and optional
- **Inequality-aware** — No assumption of universal textbook access
- **Supportive, not authoritarian** — Materials inform planning, never drive it
- **No forced digital adoption** — Physical and digital materials treated equally
- **No completion enforcement** — Page ranges are reference, not requirements
- **Phase isolation** — Phase 3 may read Phase 0, 1, and 2 data but must not mutate them directly

## Glossary

- **Textbook**: A physical or digital instructional resource (optional reference material)
- **Content_Mapping**: An association between a curriculum topic and textbook content
- **Page_Range**: A reference to specific pages in a textbook (optional)
- **Exercise_Reference**: A reference to practice problems or activities (optional)
- **Workload_Estimate**: A teacher-provided estimate of student work required (optional)
- **Lesson_Content_Alignment**: An optional association between a lesson plan and mapped content

## Scope of Phase 3

### Included
- Optional textbook registration
- Topic-to-content mapping (page ranges, exercises)
- Workload estimation (pages, exercises, estimated time)
- Lesson-to-content alignment (optional)
- Read-only use of Phase 0, 1, and 2 data

### Explicitly Excluded
- Mandatory textbook selection
- Automatic content generation
- Digital textbook hosting or delivery
- Student-facing content access
- Enforcement of page completion
- Assumption of universal access
- Curriculum authoring or editing

## Requirements

### Requirement 1: Textbook Entity Definition

**User Story:** As a teacher, I want to optionally register textbooks I use, so that I can reference them in my planning.

#### Acceptance Criteria

1. THE System SHALL define a Textbook entity with a unique identifier
2. THE System SHALL define a Textbook entity with title, edition, and publisher attributes
3. THE System SHALL define a Textbook entity with a relationship to a Subject
4. THE System SHALL define a Textbook entity with optional ISBN and publication year
5. THE System SHALL treat textbook registration as optional
6. THE System SHALL NOT require textbook selection for any planning operation
7. THE System SHALL support both physical and digital textbooks without distinction

### Requirement 2: Content Mapping Definition

**User Story:** As a teacher, I want to map curriculum topics to textbook content, so that I can reference materials in my planning.

#### Acceptance Criteria

1. THE System SHALL define a Content_Mapping entity with a unique identifier
2. THE System SHALL define a Content_Mapping entity with a relationship to a Curriculum_Topic
3. THE System SHALL define a Content_Mapping entity with a relationship to a Textbook
4. THE System SHALL define a Content_Mapping entity with optional page range attributes (start page, end page)
5. THE System SHALL define a Content_Mapping entity with optional exercise references
6. THE System SHALL define a Content_Mapping entity with optional workload estimates
7. THE System SHALL allow multiple content mappings per topic (different textbooks, different sections)
8. THE System SHALL treat all content mapping as optional

### Requirement 3: Workload Estimation

**User Story:** As a teacher, I want to estimate workload for content, so that I can gauge realistic pacing.

#### Acceptance Criteria

1. THE System SHALL allow teachers to specify estimated pages for a content mapping
2. THE System SHALL allow teachers to specify estimated exercises for a content mapping
3. THE System SHALL allow teachers to specify estimated time (in minutes or hours) for a content mapping
4. THE System SHALL treat all workload estimates as optional
5. THE System SHALL NOT enforce workload limits or completion targets
6. THE System SHALL aggregate workload estimates for informational purposes only

### Requirement 4: Lesson Content Alignment

**User Story:** As a teacher, I want to optionally associate lesson plans with content mappings, so that I can track what materials I'm using.

#### Acceptance Criteria

1. THE System SHALL allow optional association between Lesson_Plans and Content_Mappings
2. THE System SHALL allow multiple content mappings per lesson plan
3. THE System SHALL allow lesson plans to exist without content mappings
4. THE System SHALL NOT require content mapping for lesson plan creation
5. THE System SHALL display associated content when viewing lesson plans (if mappings exist)

### Requirement 5: Workload Aggregation

**User Story:** As a teacher, I want to see aggregated workload estimates, so that I can understand total student work required.

#### Acceptance Criteria

1. THE System SHALL calculate total estimated pages for a planning period
2. THE System SHALL calculate total estimated exercises for a planning period
3. THE System SHALL calculate total estimated time for a planning period
4. THE System SHALL present workload aggregates as informational only
5. THE System SHALL NOT enforce workload limits
6. THE System SHALL exclude lesson plans without content mappings from aggregation

### Requirement 6: Read-Only Access to Phase 0, 1, and 2 Data

**User Story:** As a system owner, I want Phase 3 to respect existing data, so that content mapping remains a supportive layer.

#### Acceptance Criteria

1. THE System SHALL read Curriculum_Topics for content mapping (read-only)
2. THE System SHALL read Lesson_Plans for content alignment (read-only)
3. THE System SHALL read Subjects for textbook association (read-only)
4. THE System SHALL NOT modify Phase 0, 1, or 2 entities
5. THE System SHALL treat content mapping as annotation, not mutation

### Requirement 7: Inequality Awareness

**User Story:** As a system owner, I want to ensure the system never assumes universal textbook access, so that it remains equitable.

#### Acceptance Criteria

1. THE System SHALL NOT require textbook selection for any operation
2. THE System SHALL NOT flag missing textbooks as errors
3. THE System SHALL NOT assume students have access to registered textbooks
4. THE System SHALL treat textbook references as teacher planning aids only
5. THE System SHALL NOT generate student-facing content from textbook mappings
6. THE System SHALL allow teachers to plan without any textbook references

### Requirement 8: Non-Destructive Behavior

**User Story:** As a system owner, I want to ensure Phase 3 cannot damage existing data.

#### Acceptance Criteria

1. THE System SHALL NOT mutate Phase 0, 1, or 2 records directly
2. THE System SHALL treat content mappings as separate, optional entities
3. THE System SHALL allow deletion of textbooks and content mappings without affecting lesson plans
4. THE System SHALL maintain referential integrity at all times

## Assumptions

- Not all teachers use textbooks
- Not all students have access to textbooks
- Textbook access may vary by student (inequality exists)
- Teachers may use multiple textbooks or no textbooks
- Physical and digital textbooks are equally valid
- Page ranges are reference material, not completion requirements
- Workload estimates are approximations, not guarantees

## Out of Scope (Phase 3)

- Digital textbook hosting or delivery
- Student-facing content access
- Automatic content generation
- Enforcement of page completion
- Tracking of student textbook access
- Curriculum authoring or editing
- Integration with textbook publishers
- Digital rights management
- Content licensing

---

**End of Phase 3 Requirements**

This document defines what Phase 3 must do, what it must never do, and where authority lies. Phase 3 is strictly a supportive, optional layer that annotates plans without driving them. Once approved, these requirements should be frozen before design or implementation begins.
