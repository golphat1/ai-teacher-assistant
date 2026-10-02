from unittest.mock import patch

from app.tests.test_assessments_submissions import _create_assessment_and_assignment, _full_setup, _register_and_login
from app.tests.test_submission_analysis import _analysis_result, _submit_answer


def _analyze(client, submission_id, question_id, headers_t):
    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(_analysis_result(question_id), {"prompt_tokens": 10, "completion_tokens": 10, "latency_ms": 5}, "anthropic", "v1"),
    ):
        return client.post(f"/submissions/{submission_id}/analyze", headers=headers_t)


def test_analytics_snapshot_is_cached_on_second_call(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    first = client.get(f"/classes/{ctx['class_id']}/analytics", headers=headers_t).json()
    assert first["is_cached"] is False

    second = client.get(f"/classes/{ctx['class_id']}/analytics", headers=headers_t).json()
    assert second["is_cached"] is True
    assert second["generated_at"] == first["generated_at"]


def test_analytics_force_refresh_recomputes(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    client.get(f"/classes/{ctx['class_id']}/analytics", headers=headers_t)
    refreshed = client.get(f"/classes/{ctx['class_id']}/analytics?refresh=true", headers=headers_t).json()
    assert refreshed["is_cached"] is False


def test_submissions_table_review_status_transitions(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    rows = client.get(f"/classes/{ctx['class_id']}/submissions-table", headers=headers_t).json()
    assert rows[0]["review_status"] == "not_analyzed"

    _analyze(client, submission["id"], question_id, headers_t)
    rows = client.get(f"/classes/{ctx['class_id']}/submissions-table", headers=headers_t).json()
    assert rows[0]["review_status"] == "pending"

    client.post(f"/submissions/{submission['id']}/review", headers=headers_t)
    rows = client.get(f"/classes/{ctx['class_id']}/submissions-table", headers=headers_t).json()
    assert rows[0]["review_status"] == "reviewed"


def test_concept_priorities_blocks_non_owning_teacher(client, db_session):
    """Regression test for the Stage 10 gap fixed in Stage 11."""
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    _create_assessment_and_assignment(client, ctx, headers_t)

    other_token, _ = _register_and_login(client, db_session, role="teacher", email="other-teacher@example.com", school_id=ctx["school_id"])
    response = client.get(f"/classes/{ctx['class_id']}/concept-priorities", headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 404