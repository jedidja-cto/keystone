# Requirements Document: Aggregation & Reporting (Phase 5)

## Introduction

Phase 5 introduces **Parent-Readable Reports**. Building upon the foundational data (Phase 0), core operations (Phase 1), and qualitative insights (Phase 4), this phase focuses on synthesizing information into a structured format suitable for sharing with parents or guardians.

In alignment with Keystone's core philosophy, reports are **interpretive and supportive**. They don't just dump raw data; they provide context and highlight the teacher's qualitative professional judgment.

**Success Criteria:** Phase 5 is successful if:
1. Teachers can generate a term-level summary for a specific student.
2. The report combines quantitative marks with curated qualitative observations.
3. The output is structured as a "snapshot" of student progress across subjects.

## Core Principles (Non-Negotiable)

- **Curation over Dumping** — Reports should highlight key trends, not every single raw mark.
- **Contextual Awareness** — Quantitative marks should be presented alongside class averages to provide context.
- **Qualitative Integration** — Teacher observations from Phase 4 are integrated to provide a holistic view.
- **Phase-Integrated** — Reports draw from Phase 1 (Assessments), Phase 2 (Curriculum), and Phase 4 (Observations).

## Glossary

- **Student Progress Report**: A synthesized summary of a student's performance and behavior over a defined period (e.g., a term).
- **Subject Performance**: A summary of marks and comments for a specific subject.
- **Curated Observations**: A selected list of qualitative notes meant for external viewing.

## Scope of Phase 5

### Included
- Generating a "Progress Report" data structure for a student.
- Aggregating marks by subject and term.
- Calculating subject averages and comparing with class averages.
- Including qualitative observations filtered for report-worthiness.
- Defining a report "template" structure (as a dictionary/JSON).

### Explicitly Excluded
- PDF generation or printer-friendly layouts (handled by future export layers).
- Emailing reports directly to parents.
- Parent login portals.
- Predictive grade modeling.

## Requirements

### Requirement 1: Progress Report Generation

**User Story:** As a teacher, I want to generate a progress report for a student for the current term, so that I can prepare for parent-teacher conferences.

#### Acceptance Criteria
1. THE System SHALL provide a `ReportGenerationService`.
2. THE System SHALL support generating a report for a specific `student_id` and `term_id`.
3. THE Report SHALL include the student's personal metadata (Name, Grade).
4. THE Report SHALL contain a list of `subject_summaries`.

### Requirement 2: Subject Summaries

**User Story:** As a parent, I want to see my child's performance in each subject along with their teacher's notes.

#### Acceptance Criteria
1. EACH `subject_summary` SHALL include:
    - Subject Name.
    - Student's average mark in that subject for the term.
    - Class average for the same subject/term.
    - A list of recent qualitative observations categorized as 'Academic' or 'Social'.
2. THE System SHALL allow the teacher to specify if an observation is "Reportable" (in Phase 5 iteration or via category filtering). *Initial implementation: Filter by specific categories.*

### Requirement 3: Period-Based Aggregation

**User Story:** As a school administrator, I want reports to be tied to academic terms.

#### Acceptance Criteria
1. THE System SHALL use `term` dates (Phase 0) to filter assessments and observations for the report.

### Requirement 4: Data Consistency

**User Story:** As a teacher, I want the report to update automatically if I change a mark.

#### Acceptance Criteria
1. THE System SHALL compute report data on-demand, ensuring it reflects the latest database state.

## Assumptions
- "Parent-readable" means the data is structured, labeled, and curated.
- A "Term" is the standard period for reporting.
- Qualitative observations are included based on category (e.g., 'Academic' observations are usually reportable).

## Out of Scope (Phase 5)
- Automated "Comment Bank" or generated text.
- Historical trend analysis (comparisons across academic years).

---
**End of Phase 4 Requirements**
