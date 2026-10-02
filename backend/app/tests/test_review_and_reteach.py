from unittest.mock import patch

from app.core.security import hash_password
from app.models.enums import GradeReleasePolicy, UserRole
from app.models.school import School
from app.models.user import User
from app.schemas.reteach import PedagogicalRecommendation, ReteachRecommendationAIResult
from app.tests.test_assessments_submissions import _create_assessment_and_assignment, _full_setup, _register_and_login
from app.tests.test_submission_analysis import _analysis_result, _submit_answer


def _analyze(client, submission_id, question_id, headers_t):
    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(_analysis_result(question_id), {"prompt_tokens": 10, "completion_tokens": 10, "latency_ms": 5}, "anthropic", "v1"),
    ):
        return client.post(f"/submissions/{submission_id}/analyze", headers=headers_t)


def test_requires_teacher_review_blocks_student_until_reviewed(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    # Default policy is requires_teacher_review — not released yet.
    results = client.get(f"/submissions/{submission['id']}/results", headers=headers_s).json()
    assert results["is_released"] is False

    review_resp = client.post(f"/submissions/{submission['id']}/review", headers=headers_t)
    assert review_resp.status_code == 200

    released_results = client.get(f"/submissions/{submission['id']}/results", headers=headers_s).json()
    assert released_results["is_released"] is True
    assert released_results["overall_score"] == 4.0


def test_auto_release_policy_skips_review_requirement(client, db_session):
    ctx = _full_setup(client, db_session)
    db_session.query(School).filter(School.id == ctx["school_id"]).update({"grade_release_policy": GradeReleasePolicy.AUTO_RELEASE})
    db_session.commit()

    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}
    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    results = client.get(f"/submissions/{submission['id']}/results", headers=headers_s).json()
    assert results["is_released"] is True  # released with no explicit /review call


def test_override_score_writes_audit_log(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    submission_full = client.get(f"/assignments/{assignment['id']}/submissions", headers=headers_t).json()[0]
    answer_id = submission_full["answers"][0]["id"]

    response = client.patch(
        f"/submissions/{submission['id']}/answers/{answer_id}/override-score",
        json={"new_score": 5.0, "reason": "Student's example was actually correct."},
        headers=headers_t,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["previous_score"] == 4.0
    assert body["new_score"] == 5.0

    from app.models.score_override_audit import ScoreOverrideAudit
    audit_rows = db_session.query(ScoreOverrideAudit).all()
    assert len(audit_rows) == 1


def test_concept_priorities_are_deterministic_and_no_ai_call(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    # No AIOrchestrator patch here at all — proves this endpoint makes no AI call.
    response = client.get(f"/classes/{ctx['class_id']}/concept-priorities", headers=headers_t)
    assert response.status_code == 200
    assert response.json()[0]["concept"] == "metaphor vs simile"
    assert response.json()[0]["frequency"] == 1


def test_reteach_recommendations_rejects_hallucinated_concept(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])
    _analyze(client, submission["id"], question_id, headers_t)

    fake_result = ReteachRecommendationAIResult(
        recommendations=[
            PedagogicalRecommendation(
                concept="an invented concept never in the priority list",
                why_it_matters="...", suggested_activity="...", check_for_understanding="...", follow_up_resource="...",
            )
        ]
    )
    with patch(
        "app.services.reteach_recommendation_service.AIOrchestrator.generate_reteach_recommendations",
        return_value=(fake_result, {"prompt_tokens": 5, "completion_tokens": 5, "latency_ms": 5}, "anthropic", "v1"),
    ):
        response = client.post(f"/classes/{ctx['class_id']}/reteach-recommendations", headers=headers_t)

    assert response.status_code == 502