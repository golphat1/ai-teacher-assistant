"""
Seeds a realistic classroom scenario against a RUNNING backend for the Locust
tests in this folder. A school must already exist (schools have no public
create endpoint by design — see Stage 2) — pass its ID.

    python loadtests/seed_data.py --base-url http://localhost:8000 --school-id <uuid>

Writes loadtests/seed_output.json. Never point this at a production database —
it creates real accounts and a real assignment.
"""
import argparse
import json
import uuid
from pathlib import Path

import requests


def register_and_login(base_url, role, email, password, school_id):
    requests.post(
        f"{base_url}/auth/register/{role}",
        json={"email": email, "password": password, "full_name": email.split("@")[0], "school_id": school_id},
    )
    resp = requests.post(f"{base_url}/auth/login", json={"email": email, "password": password, "school_id": school_id})
    resp.raise_for_status()
    return resp.json()["access_token"]


def seed(base_url: str, school_id: str, num_students: int, num_teachers: int):
    suffix = uuid.uuid4().hex[:8]
    password = "loadtest-supersecret1"

    teachers = []
    for i in range(num_teachers):
        token = register_and_login(base_url, "teacher", f"loadtest-teacher-{suffix}-{i}@example.com", password, school_id)
        teachers.append({"access_token": token})

    primary_headers = {"Authorization": f"Bearer {teachers[0]['access_token']}"}

    class_resp = requests.post(
        f"{base_url}/classes",
        json={"name": f"Load Test Grade 10 - {suffix}", "subject": "English", "grade": "10"},
        headers=primary_headers,
    )
    class_resp.raise_for_status()
    class_id = class_resp.json()["id"]

    students = []
    for i in range(num_students):
        token = register_and_login(base_url, "student", f"loadtest-student-{suffix}-{i}@example.com", password, school_id)
        # Need the student's user id to enroll them — re-fetch via /auth/me.
        me = requests.get(f"{base_url}/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
        requests.post(f"{base_url}/classes/{class_id}/enroll", json={"student_id": me["id"]}, headers=primary_headers)
        students.append({"access_token": token})

    lesson_resp = requests.post(
        f"{base_url}/api/v1/lesson-plans/generate",
        json={"grade": "Grade 10", "subject": "English", "topic": "Poetry", "student_count": num_students,
              "duration_minutes": 60, "ability_level": "mixed"},
        headers=primary_headers,
    )
    lesson_resp.raise_for_status()
    lesson_plan_id = lesson_resp.json()["lesson_plan_id"]

    assessment_resp = requests.post(f"{base_url}/assessments/from-lesson-plan/{lesson_plan_id}", headers=primary_headers)
    assessment_resp.raise_for_status()
    assessment = assessment_resp.json()

    assignment_resp = requests.post(
        f"{base_url}/assignments", json={"assessment_id": assessment["id"], "class_id": class_id}, headers=primary_headers
    )
    assignment_resp.raise_for_status()
    assignment_id = assignment_resp.json()["id"]

    output = {
        "teachers": teachers,
        "students": students,
        "class_id": class_id,
        "assignment_id": assignment_id,
        "questions": assessment["questions"],
    }
    Path(__file__).with_name("seed_output.json").write_text(json.dumps(output, indent=2))
    print(f"Seeded {num_teachers} teachers, {num_students} students, 1 class, 1 assignment.")
    print("Wrote loadtests/seed_output.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--school-id", required=True)
    parser.add_argument("--num-students", type=int, default=40)
    parser.add_argument("--num-teachers", type=int, default=5)
    args = parser.parse_args()
    seed(args.base_url, args.school_id, args.num_students, args.num_teachers)