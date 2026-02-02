# Requirements Document: Qualitative Observations (Phase 4)

## Introduction

Phase 4 introduces **Qualitative Observations**, allowing teachers to capture time-based, categorical insights about students that aren't represented by quantitative marks. These observations serve as a professional memory for the teacher, helping them track trends in student behavior, social interaction, and academic engagement.

In alignment with Keystone's core philosophy, qualitative observations are **internal only**. They are designed to assist the teacher's professional judgment and are never exposed as raw data to students or parents.

**Success Criteria:** Phase 4 is successful if:
1. Teachers can capture structured and free-text observations about students.
2. Observations are timestamped and categorized for easy retrieval.
3. The system remains a "teacher-first" tool where observations are private by default.

## Core Principles (Non-Negotiable)

- **Internal Only** — Observations are for the teacher's eyes only. No student or parent access.
- **Optional** — Teachers are never required to log an observation.
- **Categorical** — Observations should be tagged (e.g., Academic, Social, Behavioral) for organization.
- **Time-bound** — Every observation is associated with a specific date.
- **Non-Quantitative** — Observations describe *what* and *how*, not *how much*.

## Glossary

- **Qualitative Observation**: A descriptive record of a student's behavior or performance.
- **Observation Category**: A classification tag (e.g., "Academic Progress", "Social-Emotional").
- **Intensity/Level**: An optional, teacher-defined scale of significance (e.g., "Note", "Concern", "Success").

## Scope of Phase 4

### Included
- Creating, reading, updating, and deleting (CRUD) qualitative observations.
- Categorizing observations.
- Filtering observations by student, class, subject, and category.
- Date-based tracking of observations.

### Explicitly Excluded
- Parent or student portals for viewing observations.
- Automatic sentiment analysis or AI interpretation.
- Linking observations directly to specific assessment marks (they should remain separate).
- Reporting raw observations in parent-teacher reports (Phase 5 will handle interpreted summaries).

## Requirements

### Requirement 1: Observation Entity Definition

**User Story:** As a teacher, I want to record an observation about a student, so that I can remember specific incidents or trends.

#### Acceptance Criteria
1. THE System SHALL define a `QualitativeObservation` entity with a unique identifier.
2. THE System SHALL associate an observation with exactly one Student.
3. THE System SHALL associate an observation with exactly one Teacher (the author).
4. THE System SHALL associate an observation with an optional Class and Subject.
5. THE System SHALL record the `date` of the observation (ISO 8601).
6. THE System SHALL support a `category` field (e.g., Academic, Social, Behavioral).
7. THE System SHALL support an `observation_text` field for free-text notes (required).
8. THE System SHALL support an optional `intensity` field (e.g., 'neutral', 'positive', 'concern').

### Requirement 2: Categorization and Filtering

**User Story:** As a teacher, I want to find all academic concerns for a specific student, so that I can prepare for a meeting.

#### Acceptance Criteria
1. THE System SHALL allow filtering observations by `student_id`.
2. THE System SHALL allow filtering observations by `category`.
3. THE System SHALL allow filtering observations by date range.
4. THE System SHALL allow filtering observations by `intensity`.

### Requirement 3: Privacy and Internal Use

**User Story:** As a teacher, I want to be certain that my raw observations aren't accidentally shared with parents, so I can be honest in my professional notes.

#### Acceptance Criteria
1. THE System SHALL NOT expose any methods for student or parent access to observations.
2. THE System SHALL treat observations as teacher-owned metadata.

### Requirement 4: Data Integrity

**User Story:** As a system owner, I want to ensure that deleting a student also removes their observations.

#### Acceptance Criteria
1. THE System SHALL delete all associated observations when a Student is deleted (CASCADE).
2. THE System SHALL restrict Teacher deletion if they have authored observations (RESTRICT), similar to Phase 1.

## Assumptions
- Observations are primarily text-based.
- Teachers will use their own professional vocabulary for categories.
- High-intensity observations (e.g., "Concern") do not trigger automatic alerts; they are for teacher review.

## Out of Scope (Phase 4)
- Uploading media or documents to observations.
- Real-time notifications for observations.
- Cross-teacher shared notes (observations are per-teacher initially).

---
**End of Phase 4 Requirements**
