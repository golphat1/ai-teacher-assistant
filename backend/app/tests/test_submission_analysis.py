import uuid
from unittest.mock import patch

from app.schemas.submission_analysis import PerQuestionScore, SubmissionAnalysisAIResult
from app.tests.test_assessments_submissions import _create_assessment_and_assignment, _full_setup


def _analysis_result(question_id: str):
    return SubmissionAnalysisAIResult(
        overall_score=4.0,
        per_question_scores=[PerQuestionScore(question_id=question_id, score=4.0, comment="Good attempt.")],
        strengths=["Clear explanation."],
        weaknesses=["Missing an example."],
        misunderstood_concepts=["metaphor vs simile"],
        feedback_text="Solid understanding — add a concrete example next time.",
        recommendations=["Practice identifying metaphors in a short poem."],
    )


def _submit_answer(client, ctx, question_id, headers_s, assignment_id):
    return client.post(
        f"/assignments/{assignment_id}/submissions",
        json={"answers": [{"question_id": question_id, "answer_text": "A comparison without like or as."}]},
        headers=headers_s,
    ).json()


def test_analyze_submission_success(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(
            _analysis_result(question_id),
            {"prompt_tokens": 50, "completion_tokens": 80, "latency_ms": 10},
            "anthropic",
            "submission_analysis_v1",
        ),
    ):
        response = client.post(f"/submissions/{submission['id']}/analyze", headers=headers_t)

    assert response.status_code == 201
    body = response.json()
    assert body["overall_score"] == 4.0
    assert "metaphor vs simile" in body["misunderstood_concepts"]


def test_analyze_submission_rejects_hallucinated_question_id(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    fake_question_id = str(uuid.uuid4())  # not part of this submission at all

    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(
            _analysis_result(fake_question_id),
            {"prompt_tokens": 50, "completion_tokens": 80, "latency_ms": 10},
            "anthropic",
            "submission_analysis_v1",
        ),
    ):
        response = client.post(f"/submissions/{submission['id']}/analyze", headers=headers_t)

    assert response.status_code == 502
    
def test_get_analysis_endpoint_is_teacher_only_and_ownership_checked(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(_analysis_result(question_id), {"prompt_tokens": 10, "completion_tokens": 10, "latency_ms": 5}, "anthropic", "v1"),
    ):
        client.post(f"/submissions/{submission['id']}/analyze", headers=headers_t)

    # The student must NOT be able to see raw analysis directly — this is the exact bypass being closed.
    student_attempt = client.get(f"/submissions/{submission['id']}/analysis", headers=headers_s)
    assert student_attempt.status_code == 403

    teacher_attempt = client.get(f"/submissions/{submission['id']}/analysis", headers=headers_t)
    assert teacher_attempt.status_code == 200