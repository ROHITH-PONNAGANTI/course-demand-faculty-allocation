import unittest
from src.business_rules import (validate_assignment, validate_prerequisite,
    validate_unique_section_assignments, validate_transition, append_event)

class BusinessRuleTests(unittest.TestCase):
    def setUp(self):
        self.course = {"course_id":"CRS-000001"}
        self.section = {"course_id":"CRS-000001", "planned_enrollment":20, "capacity":30}
        self.room = {"capacity":40}
        self.faculty = {"faculty_id":"FAC-000001", "max_weekly_hours":12}
        self.availability = {"status":"AVAILABLE", "available_hours":10}
        self.assignments = [{"faculty_id":"FAC-000001", "weekly_hours":4}]

    def test_valid_assignment(self):
        self.assertEqual(validate_assignment(self.section,self.course,self.faculty,{"FAC-000001"},self.availability,self.assignments,self.room), [])
    def test_out_of_skill_set(self):
        self.assertIn("FACULTY_OUTSIDE_SKILL_SET", validate_assignment(self.section,self.course,self.faculty,set(),self.availability,self.assignments,self.room))
    def test_workload_exceeded(self):
        self.assignments.append({"faculty_id":"FAC-000001","weekly_hours":7})
        self.assertIn("WORKLOAD_EXCEEDED", validate_assignment(self.section,self.course,self.faculty,{"FAC-000001"},self.availability,self.assignments,self.room))
    def test_section_capacity_too_low(self):
        self.section["capacity"] = 10
        self.assertIn("SECTION_CAPACITY_TOO_LOW", validate_assignment(self.section,self.course,self.faculty,{"FAC-000001"},self.availability,self.assignments,self.room))
    def test_prerequisite_order(self):
        self.assertFalse(validate_prerequisite("2027S2", "2027S1"))
        self.assertTrue(validate_prerequisite("2026S2", "2027S1"))
    def test_duplicate_assignment(self):
        rows = [{"section_id":"SEC-1","faculty_id":"FAC-1"},{"section_id":"SEC-1","faculty_id":"FAC-1"}]
        self.assertIn("DUPLICATE_SECTION_ASSIGNMENT", validate_unique_section_assignments(rows))
    def test_valid_and_invalid_lifecycle(self):
        self.assertTrue(validate_transition("SECTION", "", "PROPOSED"))
        with self.assertRaises(ValueError): validate_transition("SECTION", "CANCELLED", "APPROVED")
    def test_append_only_event_history(self):
        original = []
        first = append_event(original,"SECTION","SEC-1","PROPOSED","SYSTEM","generated","2026-11-01T10:00:00")
        second = append_event(first,"SECTION","SEC-1","APPROVED","ACADEMIC_ADMIN","reviewed","2026-11-01T11:00:00")
        self.assertEqual(len(first),1)
        self.assertEqual(len(second),2)
        self.assertEqual(second[-1]["from_state"],"PROPOSED")

if __name__ == "__main__": unittest.main()
