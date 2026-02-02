# Phase 0: Foundational Data Documentation

## 1. Phase Summary

Phase 0 establishes the foundational data model for the Keystone school management system. This phase defines the core entities, their attributes, and relationships necessary to represent academic calendar data and basic institutional structures. The purpose is to create a clear, unambiguous domain model that serves as the foundation for all future development phases. No user interface, business workflows, or technology-specific implementations are included in this phase.

---

## 2. Entity Definitions

### 2.1 School

**Description:** Represents an educational institution using the Keystone system.

**Key Attributes:**
- `id` (required): Unique identifier for the school
- `name` (required): Official name of the school
- `address` (optional): Physical location of the school
- `contact_email` (optional): Primary email contact
- `contact_phone` (optional): Primary phone contact

**Required vs Optional:**
- Required: `id`, `name`
- Optional: `address`, `contact_email`, `contact_phone`

---

### 2.2 Teacher

**Description:** Represents an educator employed by a school.

**Key Attributes:**
- `id` (required): Unique identifier for the teacher
- `first_name` (required): Teacher's first name
- `last_name` (required): Teacher's last name
- `email` (optional): Teacher's email address
- `phone` (optional): Teacher's phone number
- `school_id` (required): Reference to the school where the teacher is employed

**Required vs Optional:**
- Required: `id`, `first_name`, `last_name`, `school_id`
- Optional: `email`, `phone`

---

### 2.3 Class

**Description:** Represents a group of students organized for instruction. A class is typically associated with a specific grade level and may be taught by one or more teachers.

**Key Attributes:**
- `id` (required): Unique identifier for the class
- `name` (required): Name or code for the class (e.g., "5A", "Grade 10 Biology")
- `school_id` (required): Reference to the school offering the class
- `grade_id` (required): Reference to the grade level of the class
- `academic_year` (optional): The academic year this class is active (e.g., "2024-2025")

**Required vs Optional:**
- Required: `id`, `name`, `school_id`, `grade_id`
- Optional: `academic_year`

---

### 2.4 Student

**Description:** Represents a learner enrolled in a school.

**Key Attributes:**
- `id` (required): Unique identifier for the student
- `first_name` (required): Student's first name
- `last_name` (required): Student's last name
- `date_of_birth` (optional): Student's date of birth
- `school_id` (required): Reference to the school where the student is enrolled
- `enrollment_status` (required): Current status (e.g., "active", "inactive", "graduated", "withdrawn")
- `enrollment_date` (optional): Date the student enrolled

**Required vs Optional:**
- Required: `id`, `first_name`, `last_name`, `school_id`, `enrollment_status`
- Optional: `date_of_birth`, `enrollment_date`

---

### 2.5 Subject

**Description:** Represents an area of study or course offered by a school.

**Key Attributes:**
- `id` (required): Unique identifier for the subject
- `name` (required): Name of the subject (e.g., "Mathematics", "English Literature")
- `code` (optional): Short code for the subject (e.g., "MATH101")
- `description` (optional): Detailed description of the subject
- `school_id` (required): Reference to the school offering the subject

**Required vs Optional:**
- Required: `id`, `name`, `school_id`
- Optional: `code`, `description`

---

### 2.6 Grade

**Description:** Represents a level or year of education within a school system.

**Key Attributes:**
- `id` (required): Unique identifier for the grade
- `name` (required): Name of the grade (e.g., "Grade 1", "Year 10", "Kindergarten")
- `level` (optional): Numeric ordinal for sequencing (e.g., 1, 2, 3... for Grade 1, Grade 2, Grade 3)
- `school_id` (required): Reference to the school defining the grade

**Required vs Optional:**
- Required: `id`, `name`, `school_id`
- Optional: `level`

---

### 2.7 Term

**Description:** Represents a defined period within an academic year, such as a semester, quarter, or trimester.

**Key Attributes:**
- `id` (required): Unique identifier for the term
- `name` (required): Name of the term (e.g., "Fall 2024", "Semester 1", "Q1")
- `start_date` (required): First day of the term
- `end_date` (required): Last day of the term
- `school_id` (required): Reference to the school defining the term

**Required vs Optional:**
- Required: `id`, `name`, `start_date`, `end_date`, `school_id`
- Optional: None

**Constraints:**
- `start_date` must precede `end_date`

---

### 2.8 Teaching_Day

**Description:** Represents a specific day on which instruction occurs. This allows the system to distinguish teaching days from non-teaching days (weekends, holidays, etc.).

**Key Attributes:**
- `id` (required): Unique identifier for the teaching day
- `date` (required): The specific date of the teaching day
- `term_id` (required): Reference to the term this teaching day belongs to

**Required vs Optional:**
- Required: `id`, `date`, `term_id`
- Optional: None

---

### 2.9 Holiday

**Description:** Represents a non-teaching day within the academic calendar, such as a public holiday or school closure.

**Key Attributes:**
- `id` (required): Unique identifier for the holiday
- `date` (required): The specific date of the holiday
- `name` (required): Name or description of the holiday (e.g., "Christmas Day", "Teacher Professional Development")
- `school_id` (required): Reference to the school observing the holiday

**Required vs Optional:**
- Required: `id`, `date`, `name`, `school_id`
- Optional: None

---

### 2.10 Exam_Period

**Description:** Represents a designated time range during which examinations are conducted.

**Key Attributes:**
- `id` (required): Unique identifier for the exam period
- `name` (required): Name of the exam period (e.g., "Midterm Exams", "Final Exams")
- `start_date` (required): First day of the exam period
- `end_date` (required): Last day of the exam period
- `term_id` (required): Reference to the term this exam period belongs to

**Required vs Optional:**
- Required: `id`, `name`, `start_date`, `end_date`, `term_id`
- Optional: None

**Constraints:**
- `start_date` must precede `end_date`

---

## 3. Relationships

### 3.1 School ↔ Teacher
- **Type:** One-to-Many
- **Description:** A school employs many teachers. Each teacher is employed by one school.
- **Cardinality:** 1 School : N Teachers
- **Constraint:** A teacher must be associated with exactly one school.

---

### 3.2 School ↔ Student
- **Type:** One-to-Many
- **Description:** A school enrolls many students. Each student is enrolled in one school.
- **Cardinality:** 1 School : N Students
- **Constraint:** A student must be associated with exactly one school.

---

### 3.3 School ↔ Class
- **Type:** One-to-Many
- **Description:** A school offers many classes. Each class belongs to one school.
- **Cardinality:** 1 School : N Classes
- **Constraint:** A class must be associated with exactly one school.

---

### 3.4 School ↔ Subject
- **Type:** One-to-Many
- **Description:** A school offers many subjects. Each subject is defined within one school.
- **Cardinality:** 1 School : N Subjects
- **Constraint:** A subject must be associated with exactly one school.

---

### 3.5 School ↔ Grade
- **Type:** One-to-Many
- **Description:** A school defines many grades. Each grade is defined within one school.
- **Cardinality:** 1 School : N Grades
- **Constraint:** A grade must be associated with exactly one school.

---

### 3.6 School ↔ Term
- **Type:** One-to-Many
- **Description:** A school defines many terms. Each term belongs to one school.
- **Cardinality:** 1 School : N Terms
- **Constraint:** A term must be associated with exactly one school.

---

### 3.7 School ↔ Holiday
- **Type:** One-to-Many
- **Description:** A school observes many holidays. Each holiday is defined for one school.
- **Cardinality:** 1 School : N Holidays
- **Constraint:** A holiday must be associated with exactly one school.

---

### 3.8 Grade ↔ Class
- **Type:** One-to-Many
- **Description:** A grade level contains many classes. Each class is associated with one grade level.
- **Cardinality:** 1 Grade : N Classes
- **Constraint:** A class must be associated with exactly one grade.

---

### 3.9 Term ↔ Teaching_Day
- **Type:** One-to-Many
- **Description:** A term contains many teaching days. Each teaching day belongs to one term.
- **Cardinality:** 1 Term : N Teaching_Days
- **Constraint:** A teaching day must be associated with exactly one term.

---

### 3.10 Term ↔ Exam_Period
- **Type:** One-to-Many
- **Description:** A term may contain multiple exam periods. Each exam period belongs to one term.
- **Cardinality:** 1 Term : N Exam_Periods
- **Constraint:** An exam period must be associated with exactly one term.

---

### 3.11 Student ↔ Class
- **Type:** Many-to-Many
- **Description:** A student may be enrolled in multiple classes. A class may contain multiple students.
- **Cardinality:** N Students : M Classes
- **Constraint:** This relationship requires a join/association table to represent enrollment.

---

### 3.12 Teacher ↔ Class
- **Type:** Many-to-Many
- **Description:** A teacher may teach multiple classes. A class may be taught by multiple teachers.
- **Cardinality:** N Teachers : M Classes
- **Constraint:** This relationship requires a join/association table to represent teaching assignments.

---

### 3.13 Class ↔ Subject
- **Type:** Many-to-Many
- **Description:** A class may cover multiple subjects. A subject may be taught in multiple classes.
- **Cardinality:** N Classes : M Subjects
- **Constraint:** This relationship requires a join/association table to represent subject assignments.

---

## 4. Academic Calendar Model

### 4.1 Overview

The academic calendar model represents the temporal structure of a school year. It consists of terms, teaching days, holidays, and exam periods.

### 4.2 Structure

**Term:**
- The primary unit of academic time division
- Defined by a start date and end date
- Examples: semesters (2 per year), trimesters (3 per year), quarters (4 per year)
- Each school defines its own terms

**Teaching_Day:**
- Represents individual days when instruction occurs
- Explicitly associated with a term
- Allows the system to distinguish instructional days from non-instructional days

**Holiday:**
- Represents non-teaching days
- Can occur within or outside of term boundaries
- Each school defines its own holidays (public holidays, professional development days, school-specific closures)

**Exam_Period:**
- Represents a range of dates designated for examinations
- Must fall within a term's date range
- A term may have zero, one, or multiple exam periods (e.g., midterm and final exams)

### 4.3 Assumptions

1. **School-Specific Calendars:** Each school defines its own academic calendar. There is no shared or global calendar across schools.

2. **Non-Overlapping Terms:** Terms within a single school do not overlap. A given date belongs to at most one term.

3. **Teaching Days Are Explicit:** Teaching days are explicitly defined rather than calculated. This allows flexibility for schools with non-standard schedules.

4. **Holidays Are School-Specific:** Holidays are defined per school, not globally. Different schools may observe different holidays.

5. **Exam Periods Are Optional:** A term may have zero exam periods. Not all terms require formal examination periods.

6. **Date Ranges Are Inclusive:** Start and end dates for terms and exam periods are inclusive (both dates are part of the period).

### 4.4 Regional and Institutional Differences

**Not Handled in Phase 0:**
- Multi-calendar systems (e.g., schools operating on different calendar systems simultaneously)
- Calendar templates or presets
- Automatic calculation of teaching days based on rules
- Time zones or international date handling
- Academic year rollover or archival processes

**Intentionally Deferred:**
These complexities are acknowledged but intentionally deferred to future phases when business requirements are clearer.

---

## 5. Assumptions

### 5.1 Data Model Assumptions

1. **Single School Per Entity:** Teachers, students, and classes are associated with exactly one school. Multi-school affiliations are not supported in Phase 0.

2. **Unique Identifiers:** All entities have system-generated unique identifiers. The format and generation mechanism are not specified in Phase 0.

3. **Referential Integrity:** All relationships maintain referential integrity. Deletion or modification of referenced entities must be handled (cascade, restrict, or set null behavior to be defined in implementation phase).

4. **Enrollment Status:** Student enrollment status is a simple enumeration (e.g., "active", "inactive", "graduated", "withdrawn"). Complex enrollment workflows are not defined in Phase 0.

5. **Grade Levels Are School-Specific:** Each school defines its own grade levels. There is no standardized grade naming or sequencing across schools.

6. **Subjects Are School-Specific:** Each school defines its own subjects. There is no shared subject catalog across schools.

### 5.2 Academic Calendar Assumptions

1. **Terms Do Not Overlap:** Within a single school, terms are sequential and non-overlapping.

2. **Teaching Days Are Explicit:** Teaching days are explicitly defined in the database rather than calculated from rules.

3. **Holidays Are Dates Only:** Holidays are represented as single dates. Multi-day holiday periods are represented as multiple holiday records.

4. **Exam Periods Are Within Terms:** Exam periods must fall entirely within the date range of their associated term.

### 5.3 Scope Assumptions

1. **No Authentication or Authorization:** User accounts, roles, and permissions are not defined in Phase 0.

2. **No Audit or History:** Change tracking, versioning, and audit logs are not defined in Phase 0.

3. **No Localization:** Multi-language support and localization are not defined in Phase 0.

4. **No File Attachments:** Document storage and file attachments are not defined in Phase 0.

5. **No Communication Features:** Messaging, notifications, and announcements are not defined in Phase 0.

---

## 6. Open Questions

### 6.1 Entity Attributes

**Q1:** Should teachers have an employment status field (e.g., "full-time", "part-time", "substitute")?
- **Impact:** May affect future scheduling or reporting features
- **Decision Required:** Yes/No, and if yes, what are the valid values?

**Q2:** Should students have a student ID number separate from the system-generated unique identifier?
- **Impact:** Many schools use human-readable student IDs for administrative purposes
- **Decision Required:** Yes/No, and if yes, is it required or optional?

**Q3:** Should classes have a capacity or maximum enrollment attribute?
- **Impact:** May affect future enrollment workflows
- **Decision Required:** Yes/No, and if yes, is it required or optional?

### 6.2 Relationships

**Q4:** Can a student be enrolled in classes from different grade levels?
- **Impact:** Affects whether students have a direct relationship to a grade or only through classes
- **Decision Required:** Yes/No

**Q5:** Should there be a direct relationship between students and grades, or only through class enrollment?
- **Impact:** Affects data model structure and query patterns
- **Decision Required:** Direct relationship or indirect only?

**Q6:** Can a teacher teach classes in different grade levels?
- **Impact:** Already supported by current model, but worth confirming
- **Decision Required:** Confirm this is acceptable

### 6.3 Academic Calendar

**Q7:** Should teaching days include additional metadata (e.g., day type: "regular", "half-day", "assembly")?
- **Impact:** May affect future scheduling or attendance features
- **Decision Required:** Yes/No, and if yes, what metadata?

**Q8:** Should exam periods be associated with specific subjects or classes, or remain general?
- **Impact:** Affects granularity of exam scheduling
- **Decision Required:** General or subject/class-specific?

**Q9:** How should the system handle overlapping holidays and teaching days (e.g., a teaching day that is later declared a holiday)?
- **Impact:** Affects data integrity rules
- **Decision Required:** Define precedence or validation rules

### 6.4 Data Integrity

**Q10:** What should happen when a school is deleted?
- **Impact:** Affects all related entities (teachers, students, classes, etc.)
- **Decision Required:** Cascade delete, restrict deletion, or soft delete?

**Q11:** What should happen when a grade is deleted?
- **Impact:** Affects classes associated with that grade
- **Decision Required:** Cascade delete, restrict deletion, or require reassignment?

**Q12:** What should happen when a term is deleted?
- **Impact:** Affects teaching days and exam periods associated with that term
- **Decision Required:** Cascade delete or restrict deletion?

### 6.5 Scope Clarifications

**Q13:** Are there any additional entities that should be included in Phase 0?
- **Examples:** Departments, campuses, parent/guardian entities
- **Decision Required:** Confirm Phase 0 scope is complete

**Q14:** Should Phase 0 include any validation rules beyond date range constraints?
- **Examples:** Name format validation, email format validation
- **Decision Required:** Define validation scope for Phase 0

---

## End of Phase 0 Documentation

This document is ready for review and approval. No implementation, technology selection, or design decisions have been made. All open questions are explicitly flagged for resolution before proceeding to subsequent phases.
