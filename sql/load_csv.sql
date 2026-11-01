-- Run from the project root using a MySQL client with LOCAL INFILE enabled.
-- Example: mysql --local-infile=1 -u root -p < sql/load_csv.sql
USE course_planning;
SET FOREIGN_KEY_CHECKS = 1;
START TRANSACTION;

LOAD DATA LOCAL INFILE 'data/Program.csv' INTO TABLE Program
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(program_id,program_name,department,level,duration_years,status);

LOAD DATA LOCAL INFILE 'data/Faculty.csv' INTO TABLE Faculty
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(faculty_id,faculty_name,home_department,employment_type,max_weekly_hours,status);

LOAD DATA LOCAL INFILE 'data/Room.csv' INTO TABLE Room
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(room_id,room_name,campus,capacity,room_type,status);

LOAD DATA LOCAL INFILE 'data/Course.csv' INTO TABLE Course
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(course_id,program_id,course_name,credits,course_level,modality,is_elective,is_popular,status,weekly_contact_hours);

LOAD DATA LOCAL INFILE 'data/Prerequisite.csv' INTO TABLE Prerequisite
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(prerequisite_id,course_id,required_course_id,minimum_grade,effective_from,@effective_to)
SET effective_to = NULLIF(@effective_to,'');

LOAD DATA LOCAL INFILE 'data/FacultySkill.csv' INTO TABLE FacultySkill
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(faculty_skill_id,faculty_id,skill_name,proficiency,valid_from,@valid_to)
SET valid_to = NULLIF(@valid_to,'');

LOAD DATA LOCAL INFILE 'data/Availability.csv' INTO TABLE Availability
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(availability_id,faculty_id,term,status,available_hours,effective_from,@effective_to)
SET effective_to = NULLIF(@effective_to,'');

LOAD DATA LOCAL INFILE 'data/StudentPlan.csv' INTO TABLE StudentPlan
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(student_plan_id,student_ref,program_id,course_id,target_term,plan_status,created_at);

LOAD DATA LOCAL INFILE 'data/StudentCourseHistory.csv' INTO TABLE StudentCourseHistory
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(history_id,student_ref,course_id,completion_term,grade);

LOAD DATA LOCAL INFILE 'data/RegistrationInterest.csv' INTO TABLE RegistrationInterest
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(registration_interest_id,@student_plan_id,course_id,term,interest_status,created_at)
SET student_plan_id = NULLIF(@student_plan_id,'');

LOAD DATA LOCAL INFILE 'outputs/Section.csv' INTO TABLE Section
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(section_id,course_id,term,scheduled_slot,room_id,capacity,planned_enrollment,section_status);

LOAD DATA LOCAL INFILE 'outputs/WorkloadAssignment.csv' INTO TABLE WorkloadAssignment
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(workload_assignment_id,section_id,faculty_id,weekly_hours,assignment_status,decision_reason);

LOAD DATA LOCAL INFILE 'outputs/unmet_demand.csv' INTO TABLE UnmetDemand
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(unmet_demand_id,course_id,term,unmet_students,reason);

LOAD DATA LOCAL INFILE 'outputs/PlanningEvent.csv' INTO TABLE PlanningEvent
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES
(entity_type,entity_id,@from_state,to_state,event_type,actor_type,reason)
SET from_state = NULLIF(@from_state,'');

COMMIT;
