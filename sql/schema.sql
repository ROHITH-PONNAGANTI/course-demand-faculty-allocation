-- MySQL 8.0+ schema. Run this before loading CSV files.
CREATE DATABASE IF NOT EXISTS course_planning CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE course_planning;

CREATE TABLE Program (
  program_id VARCHAR(16) PRIMARY KEY,
  program_name VARCHAR(120) NOT NULL,
  department VARCHAR(60) NOT NULL,
  level ENUM('UG','PG') NOT NULL,
  duration_years TINYINT UNSIGNED NOT NULL,
  status ENUM('ACTIVE','INACTIVE') NOT NULL
);

CREATE TABLE Course (
  course_id VARCHAR(16) PRIMARY KEY,
  program_id VARCHAR(16) NOT NULL,
  course_name VARCHAR(120) NOT NULL,
  credits TINYINT UNSIGNED NOT NULL,
  course_level SMALLINT UNSIGNED NOT NULL,
  modality ENUM('LECTURE','LAB','SEMINAR') NOT NULL,
  is_elective BOOLEAN NOT NULL,
  is_popular BOOLEAN NOT NULL,
  status ENUM('ACTIVE','INACTIVE') NOT NULL,
  weekly_contact_hours TINYINT UNSIGNED NOT NULL,
  CONSTRAINT fk_course_program FOREIGN KEY (program_id) REFERENCES Program(program_id)
);

CREATE TABLE Prerequisite (
  prerequisite_id VARCHAR(16) PRIMARY KEY,
  course_id VARCHAR(16) NOT NULL,
  required_course_id VARCHAR(16) NOT NULL,
  minimum_grade ENUM('D','C','B','A') NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE NULL,
  CONSTRAINT fk_pre_course FOREIGN KEY (course_id) REFERENCES Course(course_id),
  CONSTRAINT fk_pre_required FOREIGN KEY (required_course_id) REFERENCES Course(course_id),
  CONSTRAINT uq_course_prereq UNIQUE (course_id, required_course_id),
  CONSTRAINT chk_not_self_prereq CHECK (course_id <> required_course_id)
);

CREATE TABLE StudentPlan (
  student_plan_id VARCHAR(16) PRIMARY KEY,
  student_ref VARCHAR(16) NOT NULL,
  program_id VARCHAR(16) NOT NULL,
  course_id VARCHAR(16) NOT NULL,
  target_term VARCHAR(8) NOT NULL,
  plan_status ENUM('DRAFT','CONFIRMED','CANCELLED') NOT NULL,
  created_at DATE NOT NULL,
  CONSTRAINT fk_plan_program FOREIGN KEY (program_id) REFERENCES Program(program_id),
  CONSTRAINT fk_plan_course FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE StudentCourseHistory (
  history_id VARCHAR(16) PRIMARY KEY,
  student_ref VARCHAR(16) NOT NULL,
  course_id VARCHAR(16) NOT NULL,
  completion_term VARCHAR(8) NOT NULL,
  grade ENUM('D','C','B','A') NOT NULL,
  CONSTRAINT fk_history_course
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
  INDEX idx_student_course (student_ref, course_id)
);

CREATE TABLE RegistrationInterest (
  registration_interest_id VARCHAR(20) PRIMARY KEY,
  student_plan_id VARCHAR(16) NULL,
  course_id VARCHAR(16) NOT NULL,
  term VARCHAR(8) NOT NULL,
  interest_status ENUM('SUBMITTED','CONFIRMED','WITHDRAWN') NOT NULL,
  created_at DATE NOT NULL,
  CONSTRAINT fk_interest_plan FOREIGN KEY (student_plan_id) REFERENCES StudentPlan(student_plan_id),
  CONSTRAINT fk_interest_course FOREIGN KEY (course_id) REFERENCES Course(course_id),
  INDEX idx_interest_course_term (course_id, term, interest_status)
);

CREATE TABLE Faculty (
  faculty_id VARCHAR(16) PRIMARY KEY,
  faculty_name VARCHAR(100) NOT NULL,
  home_department VARCHAR(60) NOT NULL,
  employment_type ENUM('FULL_TIME','CONTRACT') NOT NULL,
  max_weekly_hours TINYINT UNSIGNED NOT NULL,
  status ENUM('ACTIVE','INACTIVE') NOT NULL
);

CREATE TABLE FacultySkill (
  faculty_skill_id VARCHAR(16) PRIMARY KEY,
  faculty_id VARCHAR(16) NOT NULL,
  skill_name VARCHAR(60) NOT NULL,
  proficiency ENUM('INTERMEDIATE','ADVANCED','EXPERT') NOT NULL,
  valid_from DATE NOT NULL,
  valid_to DATE NULL,
  CONSTRAINT fk_skill_faculty FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id),
  CONSTRAINT uq_faculty_skill UNIQUE (faculty_id, skill_name, valid_from)
);

CREATE TABLE Availability (
  availability_id VARCHAR(16) PRIMARY KEY,
  faculty_id VARCHAR(16) NOT NULL,
  term VARCHAR(8) NOT NULL,
  status ENUM('AVAILABLE','LEAVE') NOT NULL,
  available_hours TINYINT UNSIGNED NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE NULL,
  CONSTRAINT fk_availability_faculty FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id),
  CONSTRAINT uq_faculty_term UNIQUE (faculty_id, term)
);

CREATE TABLE Room (
  room_id VARCHAR(16) PRIMARY KEY,
  room_name VARCHAR(80) NOT NULL,
  campus VARCHAR(30) NOT NULL,
  capacity SMALLINT UNSIGNED NOT NULL,
  room_type ENUM('LECTURE','LAB','SEMINAR') NOT NULL,
  status ENUM('ACTIVE','INACTIVE') NOT NULL
);

CREATE TABLE Section (
  section_id VARCHAR(20) PRIMARY KEY,
  course_id VARCHAR(16) NOT NULL,
  term VARCHAR(8) NOT NULL,
  scheduled_slot VARCHAR(10) NOT NULL,
  room_id VARCHAR(16) NOT NULL,
  capacity SMALLINT UNSIGNED NOT NULL,
  planned_enrollment SMALLINT UNSIGNED NOT NULL,
  section_status ENUM('PROPOSED','APPROVED','CANCELLED') NOT NULL,
  CONSTRAINT fk_section_course FOREIGN KEY (course_id) REFERENCES Course(course_id),
  CONSTRAINT fk_section_room FOREIGN KEY (room_id) REFERENCES Room(room_id),
  CONSTRAINT chk_section_capacity CHECK (planned_enrollment <= capacity),
  CONSTRAINT uq_room_term_slot UNIQUE (room_id, term, scheduled_slot)
);

CREATE TABLE WorkloadAssignment (
  workload_assignment_id VARCHAR(20) PRIMARY KEY,
  section_id VARCHAR(20) NOT NULL,
  faculty_id VARCHAR(16) NOT NULL,
  weekly_hours TINYINT UNSIGNED NOT NULL,
  assignment_status ENUM('PROPOSED','APPROVED','REJECTED') NOT NULL,
  decision_reason VARCHAR(255) NOT NULL,
  CONSTRAINT fk_workload_section FOREIGN KEY (section_id) REFERENCES Section(section_id),
  CONSTRAINT fk_workload_faculty FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id),
  CONSTRAINT uq_section_assignment UNIQUE (section_id)
);

-- Append-only audit trail: write a new event for each state transition.
CREATE TABLE PlanningEvent (
  event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  entity_type VARCHAR(40) NOT NULL,
  entity_id VARCHAR(24) NOT NULL,
  from_state VARCHAR(30) NULL,
  to_state VARCHAR(30) NOT NULL,
  event_type VARCHAR(40) NOT NULL,
  event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actor_type ENUM('LEARNER','INSTRUCTOR','ACADEMIC_ADMIN','SUPPORT','PLATFORM_ADMIN','SYSTEM') NOT NULL,
  reason VARCHAR(255) NULL,
  INDEX idx_event_entity (entity_type, entity_id, event_timestamp)
);

CREATE TABLE UnmetDemand (
  unmet_demand_id VARCHAR(16) PRIMARY KEY,
  course_id VARCHAR(16) NOT NULL,
  term VARCHAR(8) NOT NULL,
  unmet_students INT UNSIGNED NOT NULL,
  reason VARCHAR(160) NOT NULL,
  CONSTRAINT fk_unmet_course FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

-- Enforce append-only audit history: state changes are represented by new rows.
DELIMITER $$
CREATE TRIGGER trg_planning_event_no_update
BEFORE UPDATE ON PlanningEvent
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PlanningEvent is append-only; insert a new event instead';
END$$

CREATE TRIGGER trg_planning_event_no_delete
BEFORE DELETE ON PlanningEvent
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PlanningEvent is append-only; events cannot be deleted';
END$$
DELIMITER ;
