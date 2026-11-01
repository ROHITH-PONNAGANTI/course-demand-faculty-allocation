#!/usr/bin/env python3
"""Deterministic synthetic university data generator."""
import argparse, csv, json, random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def generate(scale="starter", seed=None):
    cfg = CONFIG
    rng = random.Random(cfg["seed"] if seed is None else seed)
    n = cfg[scale]
    terms = cfg["terms"]
    target = cfg["target_term"]
    out = ROOT / "data"
    out.mkdir(exist_ok=True)

    programs, courses, prerequisites = [], [], []
    faculties, skills, availability, rooms = [], [], [], []
    plans, interests, course_history = [], [], []

    departments = ["Computing", "Business", "Engineering", "Science", "Design", "Health"]
    levels = ["UG", "PG"]
    modalities = ["LECTURE", "LAB", "SEMINAR"]
    skill_pool = ["Python", "Java", "SQL", "Networks", "AI", "Statistics", "Management",
                  "Electronics", "Design", "Biology", "Cloud", "Cybersecurity"]
    elective_names = ["Applied AI", "Cloud Computing", "Data Visualization", "Cybersecurity",
                      "Product Analytics", "Entrepreneurship", "Robotics", "Digital Design"]
    popular = set()

    for i in range(1, n["programs"] + 1):
        pid = f"PRG-{i:06d}"
        dept = departments[(i-1) % len(departments)]
        programs.append({"program_id": pid, "program_name": f"{dept} Program {i:03d}",
                         "department": dept, "level": rng.choice(levels),
                         "duration_years": rng.choice([3, 4, 5]), "status": "ACTIVE"})

    course_count = n["courses"]
    for i in range(1, course_count + 1):
        cid = f"CRS-{i:06d}"
        pid = programs[(i-1) % len(programs)]["program_id"]
        if i % 10 in (7, 8):
            name = rng.choice(elective_names)
        else:
            name = f"{rng.choice(skill_pool)} Foundations {i:04d}"
        is_popular = (i % 37 == 0) or (name in elective_names and i % 3 == 0)
        if is_popular:
            popular.add(cid)
        courses.append({"course_id": cid, "program_id": pid, "course_name": name,
                        "credits": rng.choice([2, 3, 4]), "course_level": rng.choice([100, 200, 300, 400]),
                        "modality": rng.choice(modalities), "is_elective": int(i % 10 in (7, 8)),
                        "is_popular": int(is_popular), "status": "ACTIVE",
                        "weekly_contact_hours": rng.choice([2, 3, 4])})

    # Prerequisites always point from a higher-numbered course to a lower-numbered course.
    for i in range(20, course_count + 1, 13):
        prerequisites.append({"prerequisite_id": f"PRE-{len(prerequisites)+1:06d}",
                              "course_id": f"CRS-{i:06d}", "required_course_id": f"CRS-{i-3:06d}",
                              "minimum_grade": rng.choice(["D", "C", "B"]), "effective_from": "2025-01-01",
                              "effective_to": ""})

    for i in range(1, n["faculty"] + 1):
        fid = f"FAC-{i:06d}"
        primary = skill_pool[(i-1) % len(skill_pool)]
        faculties.append({"faculty_id": fid, "faculty_name": f"Faculty Member {i:04d}",
                          "home_department": departments[(i-1) % len(departments)],
                          "employment_type": rng.choice(["FULL_TIME", "CONTRACT"]),
                          "max_weekly_hours": rng.choice([12, 15, 18, 20]),
                          "status": "ACTIVE"})
        chosen = {primary}
        chosen.update(rng.sample([s for s in skill_pool if s != primary], 2))
        for skill in sorted(chosen):
            skills.append({"faculty_skill_id": f"FSK-{len(skills)+1:06d}", "faculty_id": fid,
                           "skill_name": skill, "proficiency": rng.choice(["INTERMEDIATE", "ADVANCED", "EXPERT"]),
                           "valid_from": "2025-01-01", "valid_to": ""})
        # One row per term; a small share are on leave in one term.
        for term in terms:
            on_leave = (rng.random() < 0.035)
            availability.append({"availability_id": f"AVL-{len(availability)+1:07d}",
                                 "faculty_id": fid, "term": term,
                                 "status": "LEAVE" if on_leave else "AVAILABLE",
                                 "available_hours": 0 if on_leave else faculties[-1]["max_weekly_hours"],
                                 "effective_from": "2025-01-01", "effective_to": ""})

    for i in range(1, n["rooms"] + 1):
        rooms.append({"room_id": f"ROM-{i:06d}", "room_name": f"Room {i:03d}",
                      "campus": rng.choice(["NORTH", "SOUTH", "CITY"]),
                      "capacity": rng.choice([20, 30, 40, 50, 60, 80]),
                      "room_type": rng.choice(["LECTURE", "LAB", "SEMINAR"]),
                      "status": "ACTIVE"})

    # StudentPlan is a target-term plan. Each row is one student's planned course.
    for i in range(1, n["student_plans"] + 1):
        course = rng.choice(courses)
        plans.append({"student_plan_id": f"PLN-{i:07d}", "student_ref": f"STU-{i:07d}",
                      "program_id": course["program_id"], "course_id": course["course_id"],
                      "target_term": target, "plan_status": rng.choice(["DRAFT", "CONFIRMED", "CONFIRMED"]),
                      "created_at": "2026-10-01"})

    # Generate synthetic completed-course history for planned courses
    # that have prerequisites. Every generated record satisfies the
    # prerequisite so the baseline dataset passes validation.
    grade_rank = {"D": 1, "C": 2, "B": 3, "A": 4}
    prerequisite_by_course = defaultdict(list)

    for prerequisite in prerequisites:
        prerequisite_by_course[prerequisite["course_id"]].append(prerequisite)

    history_counter = 1

    for plan in plans:
        required_prerequisites = prerequisite_by_course.get(plan["course_id"], [])

        for prerequisite in required_prerequisites:
            minimum_grade = prerequisite["minimum_grade"]

            eligible_grades = [
                grade for grade, rank in grade_rank.items()
                if rank >= grade_rank[minimum_grade]
            ]

            course_history.append({
                "history_id": f"HIS-{history_counter:07d}",
                "student_ref": plan["student_ref"],
                "course_id": prerequisite["required_course_id"],
                "completion_term": "2026S1",
                "grade": rng.choice(eligible_grades)
            })

            history_counter += 1
    # Historical demand: counts vary by course; popular electives have a higher mean.
    # Historical records deliberately have no student_plan_id; target-term interest links to plans.
    interest_counter = 1
    historical_terms = terms[:-1]
    course_ids = [c["course_id"] for c in courses]
    for cid in course_ids:
        base = rng.randint(2, 8)
        if cid in popular:
            base = rng.randint(18, 45)
        elif int(cid[-6:]) % 19 == 0:
            base = rng.randint(0, 2)  # low-enrollment courses
        for t_idx, term in enumerate(historical_terms):
            count = max(0, int(base * (0.82 + 0.14*t_idx) * rng.uniform(0.75, 1.25)))
            for _ in range(count):
                interests.append({"registration_interest_id": f"INT-{interest_counter:08d}",
                                  "student_plan_id": "", "course_id": cid, "term": term,
                                  "interest_status": rng.choice(["SUBMITTED", "CONFIRMED", "WITHDRAWN"]),
                                  "created_at": f"{term[:4]}-01-15"})
                interest_counter += 1

    for plan in plans:
        interests.append({"registration_interest_id": f"INT-{interest_counter:08d}",
                          "student_plan_id": plan["student_plan_id"], "course_id": plan["course_id"],
                          "term": target, "interest_status": "CONFIRMED" if plan["plan_status"] == "CONFIRMED" else "SUBMITTED",
                          "created_at": "2026-10-15"})
        interest_counter += 1

    tables = {
        "Program": (programs, ["program_id","program_name","department","level","duration_years","status"]),
        "Course": (courses, ["course_id","program_id","course_name","credits","course_level","modality","is_elective","is_popular","status","weekly_contact_hours"]),
        "Prerequisite": (prerequisites, ["prerequisite_id","course_id","required_course_id","minimum_grade","effective_from","effective_to"]),
        "StudentPlan": (plans, ["student_plan_id","student_ref","program_id","course_id","target_term","plan_status","created_at"]),
                "StudentCourseHistory": (
            course_history,
            ["history_id", "student_ref", "course_id", "completion_term", "grade"]
        ),
        "RegistrationInterest": (interests, ["registration_interest_id","student_plan_id","course_id","term","interest_status","created_at"]),
        "Faculty": (faculties, ["faculty_id","faculty_name","home_department","employment_type","max_weekly_hours","status"]),
        "FacultySkill": (skills, ["faculty_skill_id","faculty_id","skill_name","proficiency","valid_from","valid_to"]),
        "Availability": (availability, ["availability_id","faculty_id","term","status","available_hours","effective_from","effective_to"]),
        "Room": (rooms, ["room_id","room_name","campus","capacity","room_type","status"])
    }
    for name, (rows, fields) in tables.items():
        write_csv(out / f"{name}.csv", rows, fields)

    manifest = {"seed": cfg["seed"] if seed is None else seed, "scale": scale,
                "target_term": target, "row_counts": {k: len(v[0]) for k,v in tables.items()},
                "generator": "src/generate_data.py", "provenance": "Fully synthetic; no personal or external data."}
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", choices=["starter","full"], default="starter")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    generate(args.scale, args.seed)
