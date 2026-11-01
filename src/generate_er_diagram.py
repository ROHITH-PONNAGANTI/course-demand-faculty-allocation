
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

# Table definitions: position, columns, primary key, foreign keys
tables = {
    "Program": {
        "pos": (1, 10),
        "fields": [
            "PK  program_id",
            "program_name",
            "department",
            "level",
            "duration_years",
            "status",
        ],
    },
    "Course": {
        "pos": (5, 10),
        "fields": [
            "PK  course_id",
            "FK  program_id",
            "course_name",
            "credits, course_level",
            "modality",
            "is_elective, is_popular",
            "status, weekly_contact_hours",
        ],
    },
    "Prerequisite": {
        "pos": (9, 10),
        "fields": [
            "PK  prerequisite_id",
            "FK  course_id",
            "FK  required_course_id",
            "minimum_grade",
            "effective_from, effective_to",
        ],
    },
    "StudentPlan": {
        "pos": (1, 6.5),
        "fields": [
            "PK  student_plan_id",
            "student_ref",
            "FK  program_id",
            "FK  course_id",
            "target_term",
            "plan_status",
            "created_at",
        ],
    },
    "StudentCourseHistory": {
        "pos": (5, 6.5),
        "fields": [
            "PK  history_id",
            "student_ref",
            "FK  course_id",
            "completion_term",
            "grade",
        ],
    },
    "RegistrationInterest": {
        "pos": (9, 6.5),
        "fields": [
            "PK  registration_interest_id",
            "FK  student_plan_id (nullable)",
            "FK  course_id",
            "term",
            "interest_status",
            "created_at",
        ],
    },
    "Faculty": {
        "pos": (13, 10),
        "fields": [
            "PK  faculty_id",
            "faculty_name",
            "home_department",
            "employment_type",
            "max_weekly_hours",
            "status",
        ],
    },
    "FacultySkill": {
        "pos": (17, 10),
        "fields": [
            "PK  faculty_skill_id",
            "FK  faculty_id",
            "skill_name",
            "proficiency",
            "valid_from, valid_to",
        ],
    },
    "Availability": {
        "pos": (13, 6.5),
        "fields": [
            "PK  availability_id",
            "FK  faculty_id",
            "term",
            "status",
            "available_hours",
            "effective_from, effective_to",
        ],
    },
    "Room": {
        "pos": (17, 6.5),
        "fields": [
            "PK  room_id",
            "room_name",
            "campus",
            "capacity",
            "room_type",
            "status",
        ],
    },
    "Section": {
        "pos": (5, 2.5),
        "fields": [
            "PK  section_id",
            "FK  course_id",
            "term, scheduled_slot",
            "FK  room_id",
            "capacity",
            "planned_enrollment",
            "section_status",
        ],
    },
    "WorkloadAssignment": {
        "pos": (10, 2.5),
        "fields": [
            "PK  workload_assignment_id",
            "FK  section_id",
            "FK  faculty_id",
            "weekly_hours",
            "assignment_status",
            "decision_reason",
        ],
    },
    "UnmetDemand": {
        "pos": (15, 2.5),
        "fields": [
            "PK  unmet_demand_id",
            "FK  course_id",
            "term",
            "unmet_students",
            "reason",
        ],
    },
    "PlanningEvent": {
        "pos": (15, -1),
        "fields": [
            "PK  event_id (AUTO_INCREMENT)",
            "entity_type, entity_id",
            "from_state, to_state",
            "event_type",
            "event_timestamp",
            "actor_type",
            "reason",
        ],
    },
}

# Box dimensions
BOX_W = 3.2
HEADER_H = 0.48
LINE_H = 0.27
BOX_PADDING = 0.18

fig, ax = plt.subplots(figsize=(23, 17))
ax.set_xlim(0, 21)
ax.set_ylim(-2.5, 12.5)
ax.axis("off")

# Store actual box boundaries for relationship connections
bounds = {}

def draw_table(name, data):
    x, y = data["pos"]
    fields = data["fields"]

    box_h = HEADER_H + BOX_PADDING * 2 + len(fields) * LINE_H

    # Table box
    box = FancyBboxPatch(
        (x, y - box_h),
        BOX_W,
        box_h,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=1.3,
        edgecolor="#26384A",
        facecolor="#F4F7FA",
        zorder=3,
    )
    ax.add_patch(box)

    # Header
    header = FancyBboxPatch(
        (x, y - HEADER_H),
        BOX_W,
        HEADER_H,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=0,
        facecolor="#24476B",
        zorder=4,
    )
    ax.add_patch(header)

    ax.text(
        x + BOX_W / 2,
        y - HEADER_H / 2,
        name,
        color="white",
        fontsize=10,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=5,
    )

    for i, field in enumerate(fields):
        ax.text(
            x + 0.15,
            y - HEADER_H - BOX_PADDING - i * LINE_H,
            field,
            fontsize=8.3,
            color="#172B3A",
            va="top",
            family="DejaVu Sans",
            zorder=5,
        )

    bounds[name] = {
        "left": x,
        "right": x + BOX_W,
        "top": y,
        "bottom": y - box_h,
        "center_x": x + BOX_W / 2,
        "center_y": y - box_h / 2,
    }


for name, data in tables.items():
    draw_table(name, data)


# Relationships: parent, child, cardinality label
relationships = [
    ("Program", "Course", "1 : N"),
    ("Program", "StudentPlan", "1 : N"),
    ("Course", "StudentPlan", "1 : N"),
    ("Course", "Prerequisite", "1 : N"),
    ("Course", "StudentCourseHistory", "1 : N"),
    ("StudentPlan", "RegistrationInterest", "1 : N"),
    ("Course", "RegistrationInterest", "1 : N"),
    ("Faculty", "FacultySkill", "1 : N"),
    ("Faculty", "Availability", "1 : N"),
    ("Course", "Section", "1 : N"),
    ("Room", "Section", "1 : N"),
    ("Section", "WorkloadAssignment", "1 : N"),
    ("Faculty", "WorkloadAssignment", "1 : N"),
    ("Course", "UnmetDemand", "1 : N"),
]

def connect(parent, child, label):
    p = bounds[parent]
    c = bounds[child]

    # Connect nearest horizontal or vertical sides
    dx = c["center_x"] - p["center_x"]
    dy = c["center_y"] - p["center_y"]

    if abs(dx) >= abs(dy):
        if dx >= 0:
            start = (p["right"], p["center_y"])
            end = (c["left"], c["center_y"])
        else:
            start = (p["left"], p["center_y"])
            end = (c["right"], c["center_y"])
    else:
        if dy >= 0:
            start = (p["center_x"], p["top"])
            end = (c["center_x"], c["bottom"])
        else:
            start = (p["center_x"], p["bottom"])
            end = (c["center_x"], c["top"])

    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-",
            linewidth=1.0,
            color="#60758A",
            connectionstyle="arc3,rad=0.04",
            zorder=1,
        )
    )

    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2

    ax.text(
        mid_x,
        mid_y + 0.10,
        label,
        fontsize=7,
        color="#26384A",
        ha="center",
        va="center",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85),
        zorder=2,
    )


for parent, child, label in relationships:
    connect(parent, child, label)


# Course self-referencing prerequisite relationship
prereq = bounds["Prerequisite"]
ax.annotate(
    "Course references another Course",
    xy=(prereq["center_x"], prereq["top"]),
    xytext=(10.5, 12.0),
    fontsize=8,
    ha="center",
    arrowprops=dict(arrowstyle="->", color="#A0522D"),
    color="#A0522D",
)

# PlanningEvent is polymorphic: no conventional FK connection
event = bounds["PlanningEvent"]
ax.text(
    event["center_x"],
    event["bottom"] - 0.28,
    "Polymorphic audit reference:\nentity_type + entity_id",
    fontsize=8,
    ha="center",
    va="top",
    color="#A0522D",
)

# Title and legend
ax.text(
    10.5,
    12.25,
    "COURSE DEMAND FORECASTING & FACULTY ALLOCATION SYSTEM",
    fontsize=15,
    fontweight="bold",
    ha="center",
    color="#18334D",
)

ax.text(
    10.5,
    -2.05,
    "PK = Primary Key     FK = Foreign Key     1:N = One-to-Many",
    fontsize=10,
    ha="center",
    color="#26384A",
)

fig.savefig(
    DOCS / "ER_Diagram.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

fig.savefig(
    DOCS / "ER_Diagram.pdf",
    bbox_inches="tight",
    facecolor="white",
)

plt.close(fig)

print("ER diagram generated successfully.")
print(f"PNG: {DOCS / 'ER_Diagram.png'}")
print(f"PDF: {DOCS / 'ER_Diagram.pdf'}")
print(f"Tables included: {len(tables)}")
