# Requirements Document: Teacher Core Operations (Phase 1)

## Introduction

This document defines the requirements for Phase 1 of the Keystone project. Phase 1 builds upon the foundational data structures from Phase 0 to deliver immediate, tangible value to teachers by reducing administrative workload. This phase focuses exclusively on guided lesson planning and simple assessment logging—no automation, no AI, no student-facing features, and no enforcement of curriculum standards. The objective is to make teachers' lives easier through manual but streamlined data entry and basic aggregation.

**Success Criteria:** Phase 1 is successful if:
1. A teacher can plan lessons without changing how they think
2. A teacher can log marks faster than using spreadsheets
3. The system provides immediate, understandable summaries

If these criteria are not met, Phase 1 is considered a failure.

## Glossary

- **System**: The Keystone school management platform
- **Lesson_Plan**: A teacher-created document describing instructional activities for a specific teaching period
- **Assessment**: A teacher-created evaluation instrument used to measure student performance
- **Assessment_Mark**: A numeric value recorded for a specific student on a specific assessment
- **Class_Average**: A calculated aggregate representing the mean performance of all students in a class on an assessment
- **Student_Average**: A calculated aggregate representing the mean performance of a student across multiple assessments
- **Export_Summary**: A read-only data representation suitable for external reporting
- **Teacher**: An educator employed by a school (defined in Phase 0)
- **Class**: A group of students organized for instruction (defined in Phase 0)
- **Subject**: An area of study or course (defined in Phase 0)
- **Student**: A learner enrolled in a school (defined in Phase 0)
- **Teaching_Day**: A day on which instruction occurs (defined in Phase 0)
- **Term**: A defined period within an academic year (defined in Phase 0)

## Requirements

### Requirement 1: Lesson Plan Entity Definition

**User Story:** As a teacher, I want to create lesson plans for my classes, so that I can organize my instructional activities without being constrained by curriculum requirements.

#### Acceptance Criteria

1. THE System SHALL define a Lesson_Plan entity with a unique identifier
2. THE System SHALL define a Lesson_Plan entity with a relationship to a Teacher
3. THE System SHALL define a Lesson_Plan entity with a relationship to a Class
4. THE System SHALL define a Lesson_Plan entity with a relationship to a Subject
5. THE System SHALL define a Lesson_Plan entity with a date or date range attribute
6. THE System SHALL define a Lesson_Plan entity with a free-text instructional notes attribute
7. THE System SHALL define a Lesson_Plan entity with optional metadata attributes for topic, reference materials, and duration
8. THE System SHALL define a Lesson_Plan entity with a status attribute supporting draft and finalized states
9. WHEN a Lesson_Plan is associated with a Teacher, THE System SHALL maintain referential integrity
10. WHEN a Lesson_Plan is associated with a Class, THE System SHALL maintain referential integrity
11. WHEN a Lesson_Plan is associated with a Subject, THE System SHALL maintain referential integrity

### Requirement 2: Lesson Plan Editability

**User Story:** As a teacher, I want to edit my lesson plans at any time, so that I can adapt to changing classroom needs.

#### Acceptance Criteria

1. THE System SHALL allow modification of any Lesson_Plan attribute at any time
2. THE System SHALL allow a Lesson_Plan to transition between draft and finalized states
3. THE System SHALL allow a finalized Lesson_Plan to be edited and returned to draft state
4. THE System SHALL not enforce validation of Lesson_Plan content against curriculum standards

### Requirement 3: Lesson Plan Calendar Association

**User Story:** As a teacher, I want my lesson plans to be associated with teaching days, so that I can organize my planning around the school calendar.

#### Acceptance Criteria

1. THE System SHALL allow a Lesson_Plan to be associated with a specific Teaching_Day
2. THE System SHALL allow a Lesson_Plan to be associated with a date range spanning multiple Teaching_Days
3. THE System SHALL allow a Lesson_Plan to exist without a specific date association (unscheduled draft)
4. THE System SHALL not prevent creation of Lesson_Plans for dates outside of defined Terms
5. THE System SHALL not enforce constraints on the number of Lesson_Plans per Teaching_Day

### Requirement 4: Assessment Entity Definition

**User Story:** As a teacher, I want to create assessments for my classes, so that I can record student performance.

#### Acceptance Criteria

1. THE System SHALL define an Assessment entity with a unique identifier
2. THE System SHALL define an Assessment entity with a relationship to a Teacher
3. THE System SHALL define an Assessment entity with a relationship to a Class
4. THE System SHALL define an Assessment entity with a relationship to a Subject
5. THE System SHALL define an Assessment entity with a date attribute
6. THE System SHALL define an Assessment entity with a name or title attribute
7. THE System SHALL define an Assessment entity with an optional description attribute
8. THE System SHALL define an Assessment entity with an optional maximum marks attribute
9. WHEN an Assessment is associated with a Teacher, THE System SHALL maintain referential integrity
10. WHEN an Assessment is associated with a Class, THE System SHALL maintain referential integrity
11. WHEN an Assessment is associated with a Subject, THE System SHALL maintain referential integrity

### Requirement 5: Assessment Mark Entry

**User Story:** As a teacher, I want to record numeric marks for each student on an assessment, so that I can track student performance.

#### Acceptance Criteria

1. THE System SHALL define an Assessment_Mark entity with a unique identifier
2. THE System SHALL define an Assessment_Mark entity with a relationship to an Assessment
3. THE System SHALL define an Assessment_Mark entity with a relationship to a Student
4. THE System SHALL define an Assessment_Mark entity with a numeric value attribute
5. THE System SHALL allow Assessment_Mark values to be positive numbers or zero
6. THE System SHALL allow Assessment_Mark values to be decimal numbers
7. WHEN an Assessment_Mark is associated with an Assessment, THE System SHALL maintain referential integrity
8. WHEN an Assessment_Mark is associated with a Student, THE System SHALL maintain referential integrity
9. THE System SHALL allow modification of Assessment_Mark values at any time
10. THE System SHALL allow deletion of Assessment_Mark entries

### Requirement 6: Assessment Mark Constraints

**User Story:** As a teacher, I want the system to validate mark entries, so that I can avoid data entry errors.

#### Acceptance Criteria

1. WHEN an Assessment has a maximum marks attribute defined, THE System SHALL prevent entry of Assessment_Mark values exceeding the maximum
2. WHEN an Assessment_Mark is entered, THE System SHALL ensure the Student is enrolled in the Assessment's associated Class
3. THE System SHALL prevent duplicate Assessment_Mark entries for the same Student and Assessment combination
4. THE System SHALL allow Assessment_Mark entries for Students even if no mark has been entered for other Students in the same Class

### Requirement 7: Class Average Calculation

**User Story:** As a teacher, I want to see the average mark for a class on an assessment, so that I can understand overall class performance.

#### Acceptance Criteria

1. THE System SHALL calculate a Class_Average for each Assessment
2. WHEN calculating a Class_Average, THE System SHALL compute the arithmetic mean of all Assessment_Mark values for that Assessment
3. WHEN calculating a Class_Average, THE System SHALL exclude Students with no Assessment_Mark entry
4. WHEN no Assessment_Mark entries exist for an Assessment, THE System SHALL represent the Class_Average as undefined or null
5. THE System SHALL recalculate the Class_Average when Assessment_Mark values are added, modified, or deleted

### Requirement 8: Student Average Calculation

**User Story:** As a teacher, I want to see the average mark for each student across assessments, so that I can understand individual student performance.

#### Acceptance Criteria

1. THE System SHALL calculate a Student_Average for each Student within a specific Class and Subject combination
2. WHEN calculating a Student_Average, THE System SHALL compute the arithmetic mean of all Assessment_Mark values for that Student in that Class and Subject
3. WHEN calculating a Student_Average, THE System SHALL exclude Assessments where the Student has no Assessment_Mark entry
4. WHEN no Assessment_Mark entries exist for a Student in a Class and Subject, THE System SHALL represent the Student_Average as undefined or null
5. THE System SHALL recalculate the Student_Average when Assessment_Mark values are added, modified, or deleted
6. THE System SHALL not apply weighting, normalization, or statistical adjustments to Student_Average calculations

### Requirement 9: Export Summary Data Representation

**User Story:** As a teacher, I want to export summary data, so that I can use it for reporting purposes.

#### Acceptance Criteria

1. THE System SHALL define an Export_Summary data representation containing Class_Average values
2. THE System SHALL define an Export_Summary data representation containing Student_Average values
3. THE System SHALL define an Export_Summary data representation containing Assessment metadata (name, date, maximum marks)
4. THE System SHALL define an Export_Summary data representation containing Student metadata (name, identifier)
5. THE System SHALL define an Export_Summary data representation containing Class and Subject metadata
6. THE System SHALL allow Export_Summary data to be generated for a specific Class and Subject combination
7. THE System SHALL allow Export_Summary data to be generated for a specific date range
8. THE System SHALL represent Export_Summary as a read-only data structure

### Requirement 10: Data Integrity for Phase 1 Entities

**User Story:** As a system architect, I want to maintain data integrity for Phase 1 entities, so that the system remains consistent and reliable.

#### Acceptance Criteria

1. THE System SHALL enforce uniqueness constraints on Lesson_Plan, Assessment, and Assessment_Mark identifiers
2. THE System SHALL enforce referential integrity on all relationships between Phase 1 entities and Phase 0 entities
3. WHEN a Teacher is deleted, THE System SHALL define cascade or restrict behavior for associated Lesson_Plans and Assessments
4. WHEN a Class is deleted, THE System SHALL define cascade or restrict behavior for associated Lesson_Plans and Assessments
5. WHEN a Subject is deleted, THE System SHALL define cascade or restrict behavior for associated Lesson_Plans and Assessments
6. WHEN a Student is deleted, THE System SHALL define cascade or restrict behavior for associated Assessment_Marks
7. WHEN an Assessment is deleted, THE System SHALL define cascade or restrict behavior for associated Assessment_Marks
