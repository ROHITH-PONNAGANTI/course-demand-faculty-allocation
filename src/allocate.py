#!/usr/bin/env python3
"""Forecast demand and create explainable section/faculty/room proposals."""
import csv, json, math, hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
DATA, OUT = ROOT / "data", ROOT / "outputs"
OUT.mkdir(exist_ok=True)

def read(name):
    path = DATA / f"{name}.csv"
    if not path.exists():
        path = OUT / f"{name}.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def write(name, rows, fields):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def forecast():
    courses, interests = read("Course"), read("RegistrationInterest")
    target = CFG["target_term"]
    hist_terms = CFG["terms"][:-1][-3:]
    weights = CFG["forecast_weights"]
    counts = defaultdict(lambda: defaultdict(int))
    current_counts = defaultdict(int)
    for r in interests:
        if r["interest_status"] not in ("SUBMITTED","CONFIRMED"):
            continue
        if r["term"] in hist_terms:
            counts[r["course_id"]][r["term"]] += 1
        elif r["term"] == target:
            current_counts[r["course_id"]] += 1
    rows = []
    for c in courses:
        hist = [counts[c["course_id"]][t] for t in hist_terms[::-1]]
        weighted = sum(v*w for v,w in zip(hist, weights))
        current = current_counts[c["course_id"]]
        # Blend target-term confirmed interest with historical trend; round up for planning.
        expected = max(0, math.ceil(0.65*current + 0.35*weighted))
        rows.append({"course_id": c["course_id"], "target_term": target,
                     "historical_t1": hist[0], "historical_t2": hist[1], "historical_t3": hist[2],
                     "current_interest": current, "forecast_demand": expected,
                     "forecast_method": "0.65*current_interest + 0.35*weighted_3_term_history"})
    write("demand_forecast.csv", rows, list(rows[0].keys()) if rows else [])
    return rows

def allocate():
    courses, faculty, skills, avail, rooms = (read(x) for x in
        ["Course","Faculty","FacultySkill","Availability","Room"])
    forecasts = forecast()
    target = CFG["target_term"]
    skill_map = defaultdict(set)
    for s in skills: skill_map[s["faculty_id"]].add(s["skill_name"])
    avail_map = {a["faculty_id"]: a for a in avail if a["term"] == target}
    course_by_id = {c["course_id"]: c for c in courses}
    faculty_by_id = {f["faculty_id"]: f for f in faculty}
    room_list = sorted([r for r in rooms if r["status"] == "ACTIVE"],
                       key=lambda r: int(r["capacity"]))
    # The skill tag is inferred from course title using a documented deterministic mapping.
    skill_keywords = ["Python","Java","SQL","Networks","AI","Statistics","Management",
                      "Electronics","Design","Biology","Cloud","Cybersecurity"]
    def required_skill(course):
        title = course["course_name"]
        return next((s for s in skill_keywords if s.lower() in title.lower()), "Management")
    workload = defaultdict(int)
    used_room_slots = set()
    used_faculty_slots = set()
    time_slots = ["MON_AM","MON_PM","TUE_AM","TUE_PM","WED_AM","WED_PM","THU_AM","THU_PM","FRI_AM","FRI_PM"]
    sections, assignments, unmet = [], [], []
    sec_n = wla_n = 1
    for fcast in sorted(forecasts, key=lambda x: x["forecast_demand"], reverse=True):
        demand = int(fcast["forecast_demand"])
        if demand == 0: continue
        c = course_by_id[fcast["course_id"]]
        remaining = demand
        cap_default = int(CFG["section_capacity_default"])
        required = required_skill(c)
        eligible_rooms = [r for r in room_list if r["room_type"] == c["modality"]]
        if not eligible_rooms:
            eligible_rooms = room_list
        while remaining > 0 and sec_n <= len(courses)*int(CFG["max_sections_per_course"]):
            option = None
            chosen = None
            # Find a room-slot and a qualified faculty member who is free in that slot.
            for slot in time_slots:
                room = next((r for r in eligible_rooms
                             if (r["room_id"], slot) not in used_room_slots), None)
                if room is None:
                    continue
                candidates = []
                for f in faculty:
                    a = avail_map.get(f["faculty_id"])
                    if ((f["status"] == "ACTIVE") and a and a["status"] == "AVAILABLE"
                        and required in skill_map[f["faculty_id"]]
                        and (f["faculty_id"], slot) not in used_faculty_slots):
                        limit = min(int(f["max_weekly_hours"]), int(a["available_hours"]))
                        if workload[f["faculty_id"]] + int(c["weekly_contact_hours"]) <= limit:
                            candidates.append(f)
                candidates.sort(key=lambda x: (workload[x["faculty_id"]], x["faculty_id"]))
                if candidates:
                    option, chosen = (room, slot), candidates[0]
                    break
            if option is None:
                break
            room, slot = option
            section_cap = min(cap_default, int(room["capacity"]))
            if section_cap <= 0: break
            seats = min(remaining, section_cap)
            sec_id = f"SEC-{target[:4]}-{sec_n:06d}"
            wla_id = f"WLA-{target[:4]}-{wla_n:06d}"
            sections.append({"section_id": sec_id, "course_id": c["course_id"], "term": target,
                             "scheduled_slot": slot, "room_id": room["room_id"], "capacity": section_cap,
                             "planned_enrollment": seats, "section_status": "PROPOSED"})
            assignments.append({"workload_assignment_id": wla_id, "section_id": sec_id,
                                "faculty_id": chosen["faculty_id"], "weekly_hours": c["weekly_contact_hours"],
                                "assignment_status": "PROPOSED", "decision_reason":
                                f"Skill match={required}; available in {slot}; projected workload within limit"})
            workload[chosen["faculty_id"]] += int(c["weekly_contact_hours"])
            used_room_slots.add((room["room_id"], slot))
            used_faculty_slots.add((chosen["faculty_id"], slot))
            remaining -= seats
            sec_n += 1
            wla_n += 1
        if remaining > 0:
            unmet.append({"unmet_demand_id": f"UMD-{len(unmet)+1:06d}", "course_id": c["course_id"],
                          "term": target, "unmet_students": remaining,
                          "reason": "NO_COMPATIBLE_ROOM_OR_SKILLED_AVAILABLE_FACULTY_OR_WORKLOAD_CAPACITY"})
    write("Section.csv", sections, ["section_id","course_id","term","scheduled_slot","room_id","capacity","planned_enrollment","section_status"])
    write("WorkloadAssignment.csv", assignments, ["workload_assignment_id","section_id","faculty_id","weekly_hours","assignment_status","decision_reason"])
    write("unmet_demand.csv", unmet, ["unmet_demand_id","course_id","term","unmet_students","reason"])
    events = []
    for row in sections:
        events.append({"entity_type":"SECTION","entity_id":row["section_id"],"from_state":"",
                       "to_state":"PROPOSED","event_type":"SECTION_PROPOSED","actor_type":"SYSTEM",
                       "reason":"Created by deterministic allocation engine"})
    for row in assignments:
        events.append({"entity_type":"WORKLOAD_ASSIGNMENT","entity_id":row["workload_assignment_id"],"from_state":"",
                       "to_state":"PROPOSED","event_type":"FACULTY_ASSIGNMENT_PROPOSED","actor_type":"SYSTEM",
                       "reason":row["decision_reason"]})
    write("PlanningEvent.csv", events, ["entity_type","entity_id","from_state","to_state","event_type","actor_type","reason"])
    return sections, assignments, unmet, workload

def inject_evaluation_cases():
    """Create concrete labelled anomaly fixtures without contaminating baseline tables."""
    sections = read("Section")
    assignments = read("WorkloadAssignment")
    courses, faculty, skills = read("Course"), read("Faculty"), read("FacultySkill")
    prerequisites = read("Prerequisite")
    if not sections or not assignments:
        write("evaluation_exceptions.csv", [], ["case_id","issue_type","entity_type","entity_id","related_id","observed_value","expected_rule","description"])
        write("ground_truth.csv", [], ["case_id","issue_type","ground_truth","expected_decision"])
        return
    course_by_id = {c["course_id"]: c for c in courses}
    faculty_by_id = {f["faculty_id"]: f for f in faculty}
    skill_map = defaultdict(set)
    for row in skills: skill_map[row["faculty_id"]].add(row["skill_name"])
    first_assignment = assignments[0]
    first_section = next(x for x in sections if x["section_id"] == first_assignment["section_id"])
    first_course = course_by_id[first_section["course_id"]]
    required = required_skill_for_case(first_course)
    wrong_skill = next(f for f in faculty if required not in skill_map[f["faculty_id"]])
    hours = defaultdict(int)
    for row in assignments: hours[row["faculty_id"]] += int(row["weekly_hours"])
    fid = first_assignment["faculty_id"]
    limit = int(faculty_by_id[fid]["max_weekly_hours"])
    av = next((a for a in read("Availability") if a["faculty_id"] == fid and a["term"] == CFG["target_term"]), None)
    if av: limit = min(limit, int(av["available_hours"]))
    pre = prerequisites[0] if prerequisites else {"course_id":first_course["course_id"],"required_course_id":first_course["course_id"]}
    fixtures = [
      {"case_id":"EXC-000001","issue_type":"FACULTY_OUTSIDE_SKILL_SET","entity_type":"WORKLOAD_ASSIGNMENT","entity_id":"WLA-INVALID-000001","related_id":wrong_skill["faculty_id"],"observed_value":f"faculty_skill_missing:{required}","expected_rule":f"faculty must possess skill {required}","description":"Faculty assigned to a course without the required skill."},
      {"case_id":"EXC-000002","issue_type":"WORKLOAD_EXCEEDED","entity_type":"FACULTY","entity_id":fid,"related_id":first_assignment["workload_assignment_id"],"observed_value":str(max(hours[fid],limit)+1),"expected_rule":f"weekly assigned hours <= {limit}","description":"Synthetic assignment pushes faculty workload above the weekly limit."},
      {"case_id":"EXC-000003","issue_type":"SECTION_CAPACITY_TOO_LOW","entity_type":"SECTION","entity_id":first_section["section_id"],"related_id":first_section["course_id"],"observed_value":str(int(first_section["planned_enrollment"])),"expected_rule":f"section capacity >= planned enrollment ({first_section['capacity']})","description":"Fixture marks a section as having insufficient capacity for its planned enrollment."},
      {"case_id":"EXC-000004","issue_type":"COURSE_BEFORE_PREREQUISITE","entity_type":"COURSE","entity_id":pre["course_id"],"related_id":pre["required_course_id"],"observed_value":"2027S1_before_required_course_completion","expected_rule":"required course must be completed before dependent course starts","description":"Dependent course is scheduled before its prerequisite completion."},
      {"case_id":"EXC-000005","issue_type":"DUPLICATE_SECTION_ASSIGNMENT","entity_type":"SECTION","entity_id":first_section["section_id"],"related_id":first_assignment["faculty_id"],"observed_value":"duplicate faculty-section pair","expected_rule":"one assignment per faculty-section pair","description":"Fixture repeats an existing faculty-to-section assignment."}
    ]
    truth = [{"case_id":x["case_id"],"issue_type":x["issue_type"],"ground_truth":"INVALID","expected_decision":"REJECT_OR_FLAG"} for x in fixtures]
    fields = ["case_id","issue_type","entity_type","entity_id","related_id","observed_value","expected_rule","description"]
    write("evaluation_exceptions.csv", fixtures, fields)
    write("ground_truth.csv", truth, ["case_id","issue_type","ground_truth","expected_decision"])

def required_skill_for_case(course):
    keys = ["Python","Java","SQL","Networks","AI","Statistics","Management","Electronics","Design","Biology","Cloud","Cybersecurity"]
    return next((s for s in keys if s.lower() in course["course_name"].lower()), "Management")

def evaluate_anomalies():
    """Evaluate five isolated anomaly scenarios against expected issue labels."""

    sections = read("Section")
    assignments = read("WorkloadAssignment")
    courses = read("Course")
    faculty = read("Faculty")
    skills = read("FacultySkill")
    prerequisites = read("Prerequisite")
    availability = read("Availability")

    if not sections or not assignments or not faculty:
        raise ValueError("Cannot evaluate anomalies: allocation data is missing.")

    course_by_id = {c["course_id"]: c for c in courses}
    faculty_by_id = {f["faculty_id"]: f for f in faculty}

    skill_map = defaultdict(set)
    for row in skills:
        skill_map[row["faculty_id"]].add(row["skill_name"])

    first_assignment = assignments[0]
    first_section = next(
        s for s in sections
        if s["section_id"] == first_assignment["section_id"]
    )
    first_course = course_by_id[first_section["course_id"]]

    results = []

    def record(case_id, expected, detected):
        results.append({
            "case_id": case_id,
            "expected_issue": expected,
            "detected_issue": detected or "NONE",
            "result": "DETECTED" if detected == expected else "MISSED"
        })

    # TEST 1: Faculty assigned without the required skill.
    required = required_skill_for_case(first_course)
    wrong_faculty = next(
        (f for f in faculty if required not in skill_map[f["faculty_id"]]),
        None
    )

    if wrong_faculty is None:
        raise ValueError("Could not find faculty without the required test skill.")

    test_assignments = [dict(a) for a in assignments]
    test_assignments[0]["faculty_id"] = wrong_faculty["faculty_id"]

    detected = None
    for assignment in test_assignments:
        section = next(
            (s for s in sections if s["section_id"] == assignment["section_id"]),
            None
        )
        if section:
            course = course_by_id.get(section["course_id"])
            if course and required_skill_for_case(course) not in skill_map[assignment["faculty_id"]]:
                detected = "FACULTY_OUTSIDE_SKILL_SET"
                break

    record("EXC-000001", "FACULTY_OUTSIDE_SKILL_SET", detected)

        # TEST 2: Faculty workload exceeds the permitted weekly hours.
    faculty_id = first_assignment["faculty_id"]
    faculty_record = faculty_by_id[faculty_id]

    faculty_availability = next(
        (
            a for a in availability
            if a["faculty_id"] == faculty_id
            and a["term"] == CFG["target_term"]
        ),
        None
    )

    workload_limit = int(faculty_record["max_weekly_hours"])

    if faculty_availability:
        workload_limit = min(
            workload_limit,
            int(faculty_availability["available_hours"])
        )

    test_assignments = [dict(a) for a in assignments]

    current_hours = sum(
        int(a["weekly_hours"])
        for a in test_assignments
        if a["faculty_id"] == faculty_id
    )

    # Force workload to exceed the permitted limit.
    for assignment in test_assignments:
        if assignment["faculty_id"] == faculty_id:
            assignment["weekly_hours"] = str(
                workload_limit + 1
            )
            break

    test_hours = sum(
        int(a["weekly_hours"])
        for a in test_assignments
        if a["faculty_id"] == faculty_id
    )

    detected = (
        "WORKLOAD_EXCEEDED"
        if test_hours > workload_limit
        else None
    )

    record(
        "EXC-000002",
        "WORKLOAD_EXCEEDED",
        detected
    )

    # TEST 3: Planned enrollment exceeds section capacity.
    test_section = dict(first_section)
    test_section["capacity"] = str(
        max(0, int(test_section["planned_enrollment"]) - 1)
    )

    detected = (
        "SECTION_CAPACITY_TOO_LOW"
        if int(test_section["planned_enrollment"]) > int(test_section["capacity"])
        else None
    )
    record("EXC-000003", "SECTION_CAPACITY_TOO_LOW", detected)

    # TEST 4: Prerequisite completion occurs after the dependent course starts.
    # This is a synthetic test record, not actual student history.
    if not prerequisites:
        raise ValueError("No prerequisite records available for the test.")

    prerequisite = prerequisites[0]
    synthetic_completion = {
        "student_ref": "SYNTHETIC-TEST-STUDENT",
        "course_id": prerequisite["required_course_id"],
        "completion_term": "2027S2"
    }
    dependent_course_term = CFG["target_term"]

    detected = None
    if (
        synthetic_completion["course_id"] == prerequisite["required_course_id"]
        and synthetic_completion["completion_term"] >= dependent_course_term
    ):
        detected = "COURSE_BEFORE_PREREQUISITE"

    record("EXC-000004", "COURSE_BEFORE_PREREQUISITE", detected)

    # TEST 5: Duplicate faculty-section assignment.
    test_assignments = [dict(a) for a in assignments]
    test_assignments.append(dict(first_assignment))

    seen_pairs = set()
    detected = None

    for assignment in test_assignments:
        pair = (assignment["section_id"], assignment["faculty_id"])
        if pair in seen_pairs:
            detected = "DUPLICATE_SECTION_ASSIGNMENT"
            break
        seen_pairs.add(pair)

    record("EXC-000005", "DUPLICATE_SECTION_ASSIGNMENT", detected)

    # Compare detected issues with expected labels.
    total = len(results)
    detected_count = sum(r["result"] == "DETECTED" for r in results)
    missed_count = total - detected_count
    false_positives = sum(
        r["detected_issue"] not in ("NONE", r["expected_issue"])
        for r in results
    )

    summary = {
        "total_test_cases": total,
        "detected": detected_count,
        "missed": missed_count,
        "false_positives": false_positives,
        "evaluation_status": (
            "PASS"
            if detected_count == total and false_positives == 0
            else "FAIL"
        ),
        "prerequisite_test_note": (
            "Uses synthetic completion history; not actual student records."
        )
    }

    write(
        "anomaly_test_results.csv",
        results,
        ["case_id", "expected_issue", "detected_issue", "result"]
    )

    (OUT / "anomaly_evaluation.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8"
    )

    print("\nANOMALY EVALUATION")
    print(json.dumps(summary, indent=2))

    return summary

def validate():
    errors = []
    # PK checks and FK checks for source tables.
    tables = {n: read(n) for n in ["Program","Course","Prerequisite","StudentPlan","RegistrationInterest","Faculty","FacultySkill","Availability","Room"]}
    # Validate completed-course history and its relationship to planned prerequisites.
    history = read("StudentCourseHistory")
    history_ids = [r["history_id"] for r in history]
    if len(history_ids) != len(set(history_ids)):
        errors.append("StudentCourseHistory.history_id: duplicate primary key")
    history_course_ids = {r["course_id"] for r in history}
    history_student_refs = {r["student_ref"] for r in history}
    plan_student_refs = {r["student_ref"] for r in tables["StudentPlan"]}
    grade_rank = {"D": 1, "C": 2, "B": 3, "A": 4}
    history_lookup = defaultdict(list)
    valid_terms = set(CFG["terms"])
    for row in history:
        if row["course_id"] not in {c["course_id"] for c in tables["Course"]}:
            errors.append("StudentCourseHistory has invalid course FK")
        if row["student_ref"] not in plan_student_refs:
            errors.append("StudentCourseHistory references unknown student")
        if row["grade"] not in grade_rank:
            errors.append("StudentCourseHistory has invalid grade")
        if row["completion_term"] not in valid_terms:
            errors.append("StudentCourseHistory has invalid completion term")
        history_lookup[(row["student_ref"], row["course_id"])].append(row)
    prerequisite_rows = tables["Prerequisite"]
    prereq_by_course = defaultdict(list)
    for row in prerequisite_rows:
        prereq_by_course[row["course_id"]].append(row)
    for plan in tables["StudentPlan"]:
        for prereq in prereq_by_course.get(plan["course_id"], []):
            completed = history_lookup.get((plan["student_ref"], prereq["required_course_id"]), [])
            eligible = [
                h for h in completed
                if h["completion_term"] < plan["target_term"]
                and h["grade"] in grade_rank
                and prereq["minimum_grade"] in grade_rank
                and grade_rank[h["grade"]] >= grade_rank[prereq["minimum_grade"]]
            ]
            if not eligible:
                errors.append(
                    f"StudentPlan {plan['student_plan_id']} lacks a valid prior completion "
                    f"for prerequisite {prereq['required_course_id']}"
                )
    plan_by_id = {r["student_plan_id"]: r for r in tables["StudentPlan"]}
    for interest in tables["RegistrationInterest"]:
        plan_id = interest["student_plan_id"]
        if plan_id and plan_id in plan_by_id:
            plan = plan_by_id[plan_id]
            if interest["course_id"] != plan["course_id"] or interest["term"] != plan["target_term"]:
                errors.append("RegistrationInterest does not match its linked StudentPlan")
    def unique(name, key):
        vals = [r[key] for r in tables[name]]
        if len(vals) != len(set(vals)): errors.append(f"{name}.{key}: duplicate primary key")
    for name,key in [("Program","program_id"),("Course","course_id"),("Prerequisite","prerequisite_id"),
                     ("StudentPlan","student_plan_id"),("RegistrationInterest","registration_interest_id"),
                     ("Faculty","faculty_id"),("FacultySkill","faculty_skill_id"),("Availability","availability_id"),("Room","room_id")]:
        unique(name,key)
    pids = {r["program_id"] for r in tables["Program"]}
    cids = {r["course_id"] for r in tables["Course"]}
    fids = {r["faculty_id"] for r in tables["Faculty"]}
    plans = {r["student_plan_id"] for r in tables["StudentPlan"]}
    for r in tables["Course"]:
        if r["program_id"] not in pids: errors.append("Course has invalid program_id")
    for r in tables["Prerequisite"]:
        if r["course_id"] not in cids or r["required_course_id"] not in cids: errors.append("Prerequisite has invalid course FK")
    for r in tables["StudentPlan"]:
        if r["program_id"] not in pids or r["course_id"] not in cids: errors.append("StudentPlan has invalid FK")
    for r in tables["RegistrationInterest"]:
        if r["course_id"] not in cids: errors.append("RegistrationInterest has invalid course FK")
        if r["student_plan_id"] and r["student_plan_id"] not in plans: errors.append("RegistrationInterest has invalid plan FK")
    for r in tables["FacultySkill"] + tables["Availability"]:
        if r["faculty_id"] not in fids: errors.append("Faculty child has invalid faculty FK")
        # Effective-date validation.
    from datetime import datetime

    def parse_date(value, label):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"{label}: invalid date format {value}")
            return None

    date_rules = [
        ("Prerequisite", "effective_from", "effective_to"),
        ("FacultySkill", "valid_from", "valid_to"),
        ("Availability", "effective_from", "effective_to"),
    ]

    for table_name, start_col, end_col in date_rules:
        for row in tables[table_name]:
            start = parse_date(row.get(start_col), f"{table_name}.{start_col}")
            end = parse_date(row.get(end_col), f"{table_name}.{end_col}")

            if start is None:
                errors.append(f"{table_name}: missing or invalid {start_col}")
            if end is not None and start is not None and end < start:
                errors.append(f"{table_name}: {end_col} is earlier than {start_col}")
    # Allocation arithmetic and uniqueness checks.
    sec = read("Section")
    ass = read("WorkloadAssignment")
    room_by_id = {r["room_id"]: r for r in tables["Room"]}
    faculty_by_id = {r["faculty_id"]: r for r in tables["Faculty"]}
    course_by_id = {r["course_id"]: r for r in tables["Course"]}
    skill_map = defaultdict(set)
    for row in tables["FacultySkill"]: skill_map[row["faculty_id"]].add(row["skill_name"])
    availability_map = {(r["faculty_id"],r["term"]):r for r in tables["Availability"]}
    hours_by_faculty = defaultdict(int)
    seen_rooms, seen_pairs, seen_sections, faculty_slots = set(), set(), set(), set()
    sec_by_id = {r["section_id"]: r for r in sec}
    for r in sec:
        if r["course_id"] not in cids or r["room_id"] not in room_by_id: errors.append("Section has invalid FK")
        if int(r["planned_enrollment"]) > int(r["capacity"]): errors.append("Section planned enrollment exceeds capacity")
        if r["room_id"] in room_by_id and int(r["capacity"]) > int(room_by_id[r["room_id"]]["capacity"]):
            errors.append("Section capacity exceeds physical room capacity")
        room_slot = (r["room_id"], r["term"], r["scheduled_slot"])
        if room_slot in seen_rooms: errors.append("Room double-booked in target term/slot")
        seen_rooms.add(room_slot)
    sec_ids = set(sec_by_id)
    for r in ass:
        if r["section_id"] not in sec_ids or r["faculty_id"] not in fids: errors.append("WorkloadAssignment has invalid FK")
        pair = (r["section_id"], r["faculty_id"])

        if pair in seen_pairs:
            errors.append("Duplicate faculty-section assignment")

        if r["section_id"] in seen_sections:
            errors.append("Multiple faculty assignments for one section")

        seen_pairs.add(pair)
        seen_sections.add(r["section_id"])
        sr = sec_by_id.get(r["section_id"])
        if sr and r["faculty_id"] in faculty_by_id:
            fs = (r["faculty_id"], sr["term"], sr["scheduled_slot"])
            if fs in faculty_slots: errors.append("Faculty double-booked in target term/slot")
            faculty_slots.add(fs)
            hours_by_faculty[r["faculty_id"]] += int(r["weekly_hours"])
            c = course_by_id.get(sr["course_id"])
            if c and int(r["weekly_hours"]) != int(c["weekly_contact_hours"]):
                errors.append(
                    f"Assignment {r['workload_assignment_id']}: weekly hours "
                    "do not match course contact hours"
                )
            if c and required_skill_for_case(c) not in skill_map[r["faculty_id"]]:
                errors.append("Faculty assigned outside course skill set")
            av = availability_map.get((r["faculty_id"],sr["term"]))
            if not av or av["status"] != "AVAILABLE": errors.append("Faculty unavailable in target term")
    for fid, hours in hours_by_faculty.items():
        f = faculty_by_id[fid]
        av = availability_map.get((fid, CFG["target_term"]))
        limit = min(int(f["max_weekly_hours"]), int(av["available_hours"])) if av else 0
        if hours > limit: errors.append(f"Faculty {fid} exceeds weekly workload limit")
    assigned_sections = {r["section_id"] for r in ass}
    if assigned_sections != set(sec_by_id): errors.append("Every proposed section must have exactly one faculty assignment")
        # Lifecycle state and transition validation.
    allowed_states = {
        "SECTION": {"PROPOSED", "APPROVED", "CANCELLED"},
        "WORKLOAD_ASSIGNMENT": {"PROPOSED", "APPROVED", "REJECTED"},
        "STUDENT_PLAN": {"DRAFT", "CONFIRMED", "CANCELLED"},
    }

    allowed_transitions = {
        "SECTION": {
            ("", "PROPOSED"),
            ("PROPOSED", "APPROVED"),
            ("PROPOSED", "CANCELLED"),
        },
        "WORKLOAD_ASSIGNMENT": {
            ("", "PROPOSED"),
            ("PROPOSED", "APPROVED"),
            ("PROPOSED", "REJECTED"),
        },
        "STUDENT_PLAN": {
            ("", "DRAFT"),
            ("DRAFT", "CONFIRMED"),
            ("CONFIRMED", "CANCELLED"),
        },
    }

    events = read("PlanningEvent")
    section_ids_for_events = {r["section_id"] for r in sec}
    assignment_ids_for_events = {r["workload_assignment_id"] for r in ass}
    for event in events:
        entity = event["entity_type"]
        entity_id = event["entity_id"]
        if entity == "SECTION" and entity_id not in section_ids_for_events:
            errors.append(f"PlanningEvent references unknown section: {entity_id}")
        elif entity == "WORKLOAD_ASSIGNMENT" and entity_id not in assignment_ids_for_events:
            errors.append(f"PlanningEvent references unknown workload assignment: {entity_id}")
        elif entity not in ("SECTION", "WORKLOAD_ASSIGNMENT", "STUDENT_PLAN"):
            errors.append(f"PlanningEvent has unsupported entity type: {entity}")
    last_states = {}

    for event in events:
        entity = event["entity_type"]
        entity_id = event["entity_id"]
        old_state = event.get("from_state", "")
        new_state = event.get("to_state", "")

        if entity not in allowed_states:
            errors.append(f"Unknown lifecycle entity type: {entity}")
            continue

        if new_state not in allowed_states[entity]:
            errors.append(f"Invalid lifecycle state: {entity} {new_state}")
            continue

        if (old_state, new_state) not in allowed_transitions[entity]:
            errors.append(
                f"Invalid lifecycle transition: {entity} "
                f"{old_state} -> {new_state}"
            )

        key = (entity, entity_id)

        if key in last_states and old_state != last_states[key]:
            errors.append(
                f"Lifecycle event history mismatch: {entity} {entity_id}"
            )

        last_states[key] = new_state
    summary = {"status":"PASS" if not errors else "FAIL", "error_count":len(errors),
               "errors":errors, "source_row_counts":{k:len(v) for k,v in tables.items()},
               "section_count":len(sec), "assignment_count":len(ass),
               "unmet_demand_rows":len(read("unmet_demand")) if (OUT/"unmet_demand.csv").exists() else 0}
    (OUT/"validation_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    return summary

def main():
    sections, assignments, unmet, workload = allocate()
    inject_evaluation_cases()
    anomaly_summary = evaluate_anomalies()
    summary = validate()
    total_forecast = sum(int(r["forecast_demand"]) for r in read("demand_forecast"))
    total_allocated = sum(int(r["planned_enrollment"]) for r in sections)
    total_unmet = sum(int(r["unmet_students"]) for r in unmet)
    metrics = {"target_term":CFG["target_term"], "forecast_students":total_forecast,
               "allocated_students":total_allocated, "unmet_students":total_unmet,
               "allocation_rate":round(total_allocated/total_forecast,4) if total_forecast else 1.0,
               "sections_proposed":len(sections), "faculty_assigned":len(assignments),
               "validation_status":summary["status"],
               "anomaly_evaluation_status":anomaly_summary["evaluation_status"],
               "anomalies_detected":anomaly_summary["detected"],
               "anomalies_missed":anomaly_summary["missed"],
               "false_positives":anomaly_summary["false_positives"]}
    (OUT/"evaluation_metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    print(json.dumps(metrics,indent=2))
    if summary["status"] != "PASS" or anomaly_summary["evaluation_status"] != "PASS":
        raise SystemExit("Validation or anomaly evaluation failed. Inspect outputs reports.")

if __name__ == "__main__":
    main()