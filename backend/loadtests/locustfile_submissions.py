import json
from pathlib import Path

from locust import HttpUser, task, between

SEED = json.loads(Path(__file__).with_name("seed_output.json").read_text())


class StudentSubmissionUser(HttpUser):
    """One student in a 40-student class submitting near a deadline — tests the
    burst concurrency pattern this app actually needs to survive, not a sustained
    steady load. This endpoint is deliberately NOT rate-limited (Stage 8/12
    reasoning: 40 legitimate students submitting close together must never be
    throttled) — this test proves that holds true under real concurrency."""

    wait_time = between(0, 1)

    def on_start(self):
        if not SEED["students"]:
            self.environment.runner.quit()
            return
        self.student = SEED["students"].pop()
        self.headers = {"Authorization": f"Bearer {self.student['access_token']}"}

    @task
    def submit_assignment(self):
        payload = {
            "answers": [
                {"question_id": q["id"], "answer_text": "A metaphor compares two things without using like or as."}
                for q in SEED["questions"]
            ]
        }
        with self.client.post(
            f"/assignments/{SEED['assignment_id']}/submissions",
            json=payload, headers=self.headers, catch_response=True,
            name="/assignments/[id]/submissions",
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                response.success()  # duplicate re-submission correctly rejected by the DB constraint
            else:
                response.failure(f"Unexpected status {response.status_code}: {response.text}")