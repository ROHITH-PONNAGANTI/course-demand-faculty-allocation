# Data Dictionary

## 1. Overview

This document describes the database tables, columns, relationships, data types and validation rules used by the Course Demand Forecasting and Faculty Allocation System.

- **Database:** `course_planning`
- **Database engine:** MySQL 8.0+
- **Character set:** `utf8mb4`
- **Data provenance:** Fully synthetic; no real student or faculty personal data.
- **Date format:** `YYYY-MM-DD`
- **Academic term convention:** `YYYY S1` / `YYYY S2` (stored as strings such as `2027S1`).
- **Hours:** Weekly contact or workload hours, as applicable.

Primary keys identify records uniquely. Foreign keys maintain referential integrity where defined. Application-level validation and business rules are distinguished from constraints enforced directly by MySQL.

## 2. Entity and field definitions

### 2.1 Program

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| program_id | VARCHAR(16) | Yes | Primary key; program identifier |
| program_name | VARCHAR(120) | Yes | Program name |
| department | VARCHAR(60) | Yes | Department name |
| level | ENUM | Yes | UG or PG |
| duration_years | TINYINT UNSIGNED | Yes | Program duration in years; positive value is a business rule |
| status | ENUM | Yes | ACTIVE or INACTIVE |

### 2.2 Course

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| course_id | VARCHAR(16) | Yes | Primary key |
| program_id | VARCHAR(16) | Yes | FK referencing Program |
| course_name | VARCHAR(120) | Yes | Course name |
| credits | TINYINT UNSIGNED | Yes | Course credits; intended range 1–6 |
| course_level | SMALLINT UNSIGNED | Yes | Course academic level; intended range 100–500 |
| modality | ENUM | Yes | LECTURE, LAB or SEMINAR |
| is_elective | BOOLEAN | Yes | Indicates whether the course is elective |
| is_popular | BOOLEAN | Yes | Synthetic popularity indicator |
| status | ENUM | Yes | ACTIVE or INACTIVE |
| weekly_contact_hours | TINYINT UNSIGNED | Yes | Weekly course contact hours; intended range 1–6 |

### 2.3 Prerequisite

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| prerequisite_id | VARCHAR(16) | Yes | Primary key |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| required_course_id | VARCHAR(16) | Yes | FK referencing Course |
| minimum_grade | ENUM | Yes | D, C, B or A |
| effective_from | DATE | Yes | Start of prerequisite validity |
| effective_to | DATE | No | End of validity; NULL indicates open-ended validity |

Business rules: a course cannot be its own prerequisite. A course/prerequisite pair must be unique. Effective dates should be chronologically valid.

### 2.4 StudentPlan

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| student_plan_id | VARCHAR(16) | Yes | Primary key |
| student_ref | VARCHAR(16) | Yes | Synthetic student reference |
| program_id | VARCHAR(16) | Yes | FK referencing Program |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| target_term | VARCHAR(8) | Yes | Intended academic term |
| plan_status | ENUM | Yes | DRAFT, CONFIRMED or CANCELLED |
| created_at | DATE | Yes | Plan creation date |

### 2.5 StudentCourseHistory

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| history_id | VARCHAR(16) | Yes | Primary key |
| student_ref | VARCHAR(16) | Yes | Synthetic student reference |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| completion_term | VARCHAR(8) | Yes | Academic term of course completion |
| grade | ENUM | Yes | D, C, B or A |

The composite index on student_ref and course_id supports student-course history lookups.

### 2.6 RegistrationInterest

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| registration_interest_id | VARCHAR(20) | Yes | Primary key |
| student_plan_id | VARCHAR(16) | No | Optional FK referencing StudentPlan |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| term | VARCHAR(8) | Yes | Academic term |
| interest_status | ENUM | Yes | SUBMITTED, CONFIRMED or WITHDRAWN |
| created_at | DATE | Yes | Interest creation date |

A NULL student_plan_id supports historical interest records without a corresponding target planning cohort.

### 2.7 Faculty

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| faculty_id | VARCHAR(16) | Yes | Primary key |
| faculty_name | VARCHAR(100) | Yes | Faculty name; synthetic |
| home_department | VARCHAR(60) | Yes | Faculty department |
| employment_type | ENUM | Yes | FULL_TIME or CONTRACT |
| max_weekly_hours | TINYINT UNSIGNED | Yes | Maximum weekly workload |
| status | ENUM | Yes | ACTIVE or INACTIVE |

### 2.8 FacultySkill

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| faculty_skill_id | VARCHAR(16) | Yes | Primary key |
| faculty_id | VARCHAR(16) | Yes | FK referencing Faculty |
| skill_name | VARCHAR(60) | Yes | Teaching skill or subject |
| proficiency | ENUM | Yes | INTERMEDIATE, ADVANCED or EXPERT |
| valid_from | DATE | Yes | Skill validity start date |
| valid_to | DATE | No | Skill validity end date; NULL means open-ended |

The combination of faculty_id, skill_name and valid_from must be unique.

### 2.9 Availability

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| availability_id | VARCHAR(16) | Yes | Primary key |
| faculty_id | VARCHAR(16) | Yes | FK referencing Faculty |
| term | VARCHAR(8) | Yes | Academic term |
| status | ENUM | Yes | AVAILABLE or LEAVE |
| available_hours | TINYINT UNSIGNED | Yes | Available weekly hours |
| effective_from | DATE | Yes | Availability start date |
| effective_to | DATE | No | Availability end date; NULL means open-ended |

A faculty member can have only one availability record per term under the defined unique constraint.

### 2.10 Room

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| room_id | VARCHAR(16) | Yes | Primary key |
| room_name | VARCHAR(80) | Yes | Unique room name |
| campus | VARCHAR(30) | Yes | Campus location |
| capacity | SMALLINT UNSIGNED | Yes | Physical room capacity |
| room_type | ENUM | Yes | LECTURE, LAB or SEMINAR |
| status | ENUM | Yes | ACTIVE or INACTIVE |

### 2.11 Section

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| section_id | VARCHAR(20) | Yes | Primary key |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| term | VARCHAR(8) | Yes | Academic term |
| scheduled_slot | VARCHAR(10) | Yes | Scheduled time slot, e.g. MON_AM |
| room_id | VARCHAR(16) | Yes | FK referencing Room |
| capacity | SMALLINT UNSIGNED | Yes | Planned section capacity |
| planned_enrollment | SMALLINT UNSIGNED | Yes | Planned student enrollment |
| section_status | ENUM | Yes | PROPOSED, APPROVED or CANCELLED |

MySQL enforces planned_enrollment <= capacity. The room/term/scheduled_slot combination must be unique. The allocation process must also ensure that section capacity does not exceed physical room capacity.

### 2.12 WorkloadAssignment

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| workload_assignment_id | VARCHAR(20) | Yes | Primary key |
| section_id | VARCHAR(20) | Yes | FK referencing Section |
| faculty_id | VARCHAR(16) | Yes | FK referencing Faculty |
| weekly_hours | TINYINT UNSIGNED | Yes | Assigned weekly workload hours |
| assignment_status | ENUM | Yes | PROPOSED, APPROVED or REJECTED |
| decision_reason | VARCHAR(255) | Yes | Explanation for the assignment decision |

A section/faculty pair must be unique. Faculty workload limits are evaluated by the allocation and validation logic, rather than by a database CHECK constraint.

### 2.13 PlanningEvent

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| event_id | BIGINT AUTO_INCREMENT | Yes | Primary key |
| entity_type | VARCHAR(40) | Yes | Type of entity affected |
| entity_id | VARCHAR(24) | Yes | Identifier of the affected entity |
| from_state | VARCHAR(30) | No | Previous state |
| to_state | VARCHAR(30) | Yes | New state |
| event_type | VARCHAR(40) | Yes | Type of recorded event |
| event_timestamp | TIMESTAMP | Yes | Event time; defaults to CURRENT_TIMESTAMP |
| actor_type | ENUM | Yes | LEARNER, INSTRUCTOR, ACADEMIC_ADMIN, SUPPORT, PLATFORM_ADMIN or SYSTEM |
| reason | VARCHAR(255) | No | Optional explanation |

PlanningEvent is designed as a polymorphic audit log. It does not use foreign keys to every entity table. The entity_type and entity_id combination identifies the affected record.

### 2.14 UnmetDemand

| Field | Data type | Required | Description / validation |
|---|---|---|---|
| unmet_demand_id | VARCHAR(16) | Yes | Primary key |
| course_id | VARCHAR(16) | Yes | FK referencing Course |
| term | VARCHAR(8) | Yes | Academic term |
| unmet_students | INT UNSIGNED | Yes | Number of students whose demand was not allocated |
| reason | VARCHAR(160) | Yes | Explanation for unmet demand |

## 3. Relationships and cardinality

- Program 1:N Course.
- Program 1:N StudentPlan.
- Course 1:N StudentPlan.
- Course 1:N StudentCourseHistory.
- Course 1:N RegistrationInterest.
- Course 1:N Section.
- Course 1:N UnmetDemand.
- Course N:M Course through Prerequisite, using course_id and required_course_id.
- Faculty 1:N FacultySkill.
- Faculty 1:N Availability.
- Faculty 1:N WorkloadAssignment.
- Room 1:N Section across different terms and scheduled slots.
- Section 1:N WorkloadAssignment structurally; the operational allocation policy expects one lead faculty member per section.
- StudentPlan 1:N RegistrationInterest; historical records may have a NULL StudentPlan reference.
- PlanningEvent records changes against multiple entity types through a polymorphic reference.

## 4. Lifecycle and business rules

| Entity | Allowed states | Intended transitions |
|---|---|---|
| StudentPlan | DRAFT, CONFIRMED, CANCELLED | DRAFT → CONFIRMED → CANCELLED |
| Section | PROPOSED, APPROVED, CANCELLED | PROPOSED → APPROVED or CANCELLED |
| WorkloadAssignment | PROPOSED, APPROVED, REJECTED | PROPOSED → APPROVED or REJECTED |

These ENUM values restrict the stored states, but the SQL schema does not itself enforce transition sequences. State-transition validation must be performed by application logic or additional database mechanisms.

State changes should append PlanningEvent records rather than overwrite historical event records.

## 5. Data integrity and validation

### Database-enforced constraints

- Primary key uniqueness.
- Defined foreign key references.
- ENUM restrictions.
- Unique course/prerequisite pairs.
- Prevention of self-referencing prerequisites.
- Unique faculty/skill/effective-start combinations.
- Unique faculty/term availability records.
- Unique room/term/scheduled-slot combinations.
- Section planned enrollment not exceeding section capacity.
- Unique section/faculty assignment pairs.

### Application-level business validations

- Positive program duration and valid course credit ranges.
- Valid academic term formatting.
- Chronological validity of effective dates.
- Valid lifecycle transition sequences.
- Section capacity not exceeding physical room capacity.
- Faculty skill and availability compatibility.
- Faculty workload not exceeding permitted limits.
- Prerequisite completion before planned course enrollment.
- Correct reconciliation of forecast, allocated and unmet demand.

### Data conventions

- IDs are generated as prefixed, zero-padded strings by the data-generation process; the VARCHAR primary keys do not enforce the prefix format.
- Boolean fields represent true/false indicators.
- Synthetic student references do not identify real individuals.
- Nullable foreign keys and dates may be represented by empty CSV fields during loading.
- NULL effective end dates represent open-ended validity.
## 5. Field-level constraint catalogue

The following catalogue makes uniqueness, domain/range, unit and validation expectations explicit. `Required` means non-NULL in the SQL schema unless marked optional. All IDs are immutable strings; all dates use ISO `YYYY-MM-DD`; academic terms use `YYYYS1` or `YYYYS2`.

| Entity.field | Required | Uniqueness | Allowed values / units | Validation rule |
|---|---|---|---|---|
| Program.program_id | Yes | PK | `PRG-` + 6 digits | Must be unique and referenced consistently |
| Program.program_name | Yes | No | Text, max 120 chars | Non-empty |
| Program.department | Yes | No | Text, max 60 chars | Non-empty |
| Program.level | Yes | No | UG, PG | Enum membership |
| Program.duration_years | Yes | No | Positive years | Greater than zero |
| Program.status | Yes | No | ACTIVE, INACTIVE | Enum membership |
| Course.course_id | Yes | PK | `CRS-` + 6 digits | Must be unique |
| Course.program_id | Yes | No | Program ID | Must reference Program |
| Course.course_name | Yes | No | Text, max 120 chars | Non-empty |
| Course.credits | Yes | No | 1–6 credits | Positive and within intended range |
| Course.course_level | Yes | No | 100–500 | Within intended academic-level range |
| Course.modality | Yes | No | LECTURE, LAB, SEMINAR | Enum membership |
| Course.is_elective / is_popular | Yes | No | Boolean | 0 or 1 |
| Course.status | Yes | No | ACTIVE, INACTIVE | Enum membership |
| Course.weekly_contact_hours | Yes | No | 1–6 hours/week | Positive and within intended range |
| Prerequisite.prerequisite_id | Yes | PK | PRQ ID | Unique |
| Prerequisite.course_id / required_course_id | Yes | Pair unique | Course IDs | Both must reference Course; cannot be equal |
| Prerequisite.minimum_grade | Yes | No | D, C, B, A | Enum membership and grade-rank comparison |
| Prerequisite.effective_from | Yes | No | ISO date | Valid date |
| Prerequisite.effective_to | No | No | ISO date or NULL | Must be on/after effective_from |
| StudentPlan.student_plan_id | Yes | PK | PLN ID | Unique |
| StudentPlan.student_ref | Yes | No | Synthetic student ID | Must be non-empty and consistent with history |
| StudentPlan.program_id / course_id | Yes | No | Program/Course IDs | Must reference parent records; course should belong to program |
| StudentPlan.target_term | Yes | No | Academic term | Must match configured term vocabulary |
| StudentPlan.plan_status | Yes | No | DRAFT, CONFIRMED, CANCELLED | Enum and valid transition |
| StudentPlan.created_at | Yes | No | ISO date | Valid date |
| RegistrationInterest.registration_interest_id | Yes | PK | RI ID | Unique |
| RegistrationInterest.student_plan_id | No | No | Plan ID or NULL | If present, must reference a plan and match its course/term |
| RegistrationInterest.course_id / term | Yes | No | Course ID / academic term | Course FK and valid term |
| RegistrationInterest.interest_status | Yes | No | SUBMITTED, CONFIRMED, WITHDRAWN | Enum membership |
| RegistrationInterest.created_at | Yes | No | ISO date | Valid date |
| Faculty.faculty_id | Yes | PK | `FAC-` + 6 digits | Unique |
| Faculty.faculty_name / home_department | Yes | No | Text | Non-empty |
| Faculty.employment_type | Yes | No | FULL_TIME, CONTRACT | Enum membership |
| Faculty.max_weekly_hours | Yes | No | Hours/week | Positive; allocation cannot exceed it |
| Faculty.status | Yes | No | ACTIVE, INACTIVE | Enum membership |
| FacultySkill.faculty_skill_id | Yes | PK | FSK ID | Unique |
| FacultySkill.faculty_id | Yes | No | Faculty ID | Must reference Faculty |
| FacultySkill.skill_name | Yes | Composite | Skill text | Non-empty; skill valid on assignment date |
| FacultySkill.proficiency | Yes | No | INTERMEDIATE, ADVANCED, EXPERT | Enum membership |
| FacultySkill.valid_from / valid_to | From yes; to no | Composite includes valid_from | ISO dates | End date cannot precede start date |
| Availability.availability_id | Yes | PK | AVL ID | Unique |
| Availability.faculty_id / term | Yes | Pair unique | Faculty ID / academic term | Faculty FK; one record per faculty per term |
| Availability.status | Yes | No | AVAILABLE, LEAVE | Enum membership |
| Availability.available_hours | Yes | No | Hours/week | Non-negative; assignment must fit both availability and faculty limit |
| Availability.effective_from / effective_to | From yes; to no | No | ISO dates | End date cannot precede start date |
| Room.room_id | Yes | PK | ROOM ID | Unique |
| Room.room_name | Yes | Unique | Text, max 80 chars | Unique and non-empty |
| Room.campus | Yes | No | Text | Non-empty |
| Room.capacity | Yes | No | Seats | Positive; section capacity cannot exceed it |
| Room.room_type | Yes | No | LECTURE, LAB, SEMINAR | Enum membership |
| Room.status | Yes | No | ACTIVE, INACTIVE | Enum membership |
| Section.section_id | Yes | PK | `SEC-YYYY-` + 6 digits | Unique and year matches target term |
| Section.course_id / room_id | Yes | No | Course/Room IDs | Must reference parent records |
| Section.term | Yes | No | Academic term | Valid configured term |
| Section.scheduled_slot | Yes | Room/term/slot composite | Slot code | Prevent room double-booking |
| Section.capacity / planned_enrollment | Yes | No | Seats | Enrollment <= section capacity <= room capacity |
| Section.section_status | Yes | No | PROPOSED, APPROVED, CANCELLED | Enum and valid transition |
| WorkloadAssignment.workload_assignment_id | Yes | PK | `WLA-YYYY-` + 6 digits | Unique and year matches target term |
| WorkloadAssignment.section_id | Yes | Unique in current schema | Section ID | Must reference Section; one lead assignment per section |
| WorkloadAssignment.faculty_id | Yes | No | Faculty ID | Must reference Faculty and hold required skill |
| WorkloadAssignment.weekly_hours | Yes | No | Hours/week | Sum per faculty <= min(max_weekly_hours, available_hours) |
| WorkloadAssignment.assignment_status | Yes | No | PROPOSED, APPROVED, REJECTED | Enum and valid transition |
| WorkloadAssignment.decision_reason | Yes | No | Text, max 255 chars | Must explain selection/exception |

`PlanningEvent` and `UnmetDemand` are supporting entities beyond the eleven core entities. PlanningEvent uses a polymorphic entity reference, so referential validation is performed by application logic; SQL cannot express a single FK to several possible parent tables. `event_timestamp` is generated by MySQL when omitted from an insert. The schema's append-only triggers reject UPDATE and DELETE operations on PlanningEvent.
