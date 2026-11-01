"""Reusable, side-effect-free business rules for allocation and lifecycle tests."""
from collections import defaultdict

TRANSITIONS = {
    "SECTION": {("", "PROPOSED"), ("PROPOSED", "APPROVED"), ("PROPOSED", "CANCELLED")},
    "WORKLOAD_ASSIGNMENT": {("", "PROPOSED"), ("PROPOSED", "APPROVED"), ("PROPOSED", "REJECTED")},
    "STUDENT_PLAN": {("", "DRAFT"), ("DRAFT", "CONFIRMED"), ("CONFIRMED", "CANCELLED")},
}

def validate_assignment(section, course, faculty, skills, availability, assignments, room):
    """Return a list of rule violations for one proposed faculty/section assignment."""
    errors = []
    if section["course_id"] != course["course_id"]:
        errors.append("SECTION_COURSE_MISMATCH")
    if int(section["planned_enrollment"]) > int(section["capacity"]):
        errors.append("SECTION_CAPACITY_TOO_LOW")
    if int(section["capacity"]) > int(room["capacity"]):
        errors.append("ROOM_CAPACITY_EXCEEDED")
    if faculty["faculty_id"] not in skills:
        errors.append("FACULTY_OUTSIDE_SKILL_SET")
    if availability.get("status") != "AVAILABLE":
        errors.append("FACULTY_UNAVAILABLE")
    hours = sum(int(a["weekly_hours"]) for a in assignments if a["faculty_id"] == faculty["faculty_id"])
    limit = min(int(faculty["max_weekly_hours"]), int(availability.get("available_hours", 0)))
    if hours > limit:
        errors.append("WORKLOAD_EXCEEDED")
    return errors

def validate_prerequisite(completion_term, course_term):
    return bool(completion_term and course_term and completion_term < course_term)

def validate_unique_section_assignments(assignments):
    seen, errors = set(), []
    for row in assignments:
        key = (row["section_id"], row["faculty_id"])
        if key in seen:
            errors.append("DUPLICATE_SECTION_ASSIGNMENT")
        seen.add(key)
    return errors

def validate_transition(entity_type, from_state, to_state):
    if entity_type not in TRANSITIONS or (from_state or "", to_state) not in TRANSITIONS[entity_type]:
        raise ValueError(f"Invalid lifecycle transition: {entity_type} {from_state} -> {to_state}")
    return True

def append_event(history, entity_type, entity_id, to_state, actor_type, reason, timestamp):
    """Append a transition event; never mutate or replace an earlier event."""
    previous = next((e for e in reversed(history) if e["entity_type"] == entity_type and e["entity_id"] == entity_id), None)
    old_state = previous["to_state"] if previous else ""
    validate_transition(entity_type, old_state, to_state)
    event = {"entity_type": entity_type, "entity_id": entity_id, "from_state": old_state,
             "to_state": to_state, "event_type": f"{entity_type}_{to_state}",
             "actor_type": actor_type, "reason": reason, "event_timestamp": timestamp}
    return history + [event]
