from app.repositories.submission_repository import SubmissionRepository
from app.tests.test_assessments_submissions import _create_assessment_and_assignment, _full_setup
from app.tests.test_submission_analysis import _submit_answer


def test_get_by_id_for_school_returns_submission_for_correct_school(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    from app.models.school import School
    school = db_session.query(School).filter(School.id == ctx["school_id"]).first()

    result = SubmissionRepository(db_session).get_by_id_for_school(submission["id"], school_id=school.id)
    assert result is not None
    assert str(result.id) == submission["id"]


def test_get_by_id_for_school_excludes_submission_from_other_school(client, db_session):
    """Proves the tenant gate works at the repository level, independent of any
    ownership check higher up — the actual defense-in-depth this fix adds."""
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    from app.models.school import School
    other_school = School(name="A Different School Entirely")
    db_session.add(other_school)
    db_session.commit()
    db_session.refresh(other_school)

    result = SubmissionRepository(db_session).get_by_id_for_school(submission["id"], school_id=other_school.id)
    assert result is None  # the submission exists, but not under this (wrong) school_id


def test_analyze_and_results_endpoints_still_work_end_to_end_after_the_change(client, db_session):
    """Regression check: the school-scoping addition must not break the normal,
    same-school path that every earlier stage's tests already cover."""
    from unittest.mock import patch
    from app.tests.test_submission_analysis import _analysis_result

    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    question_id = assessment["questions"][0]["id"]
    submission = _submit_answer(client, ctx, question_id, headers_s, assignment["id"])

    with patch(
        "app.services.analysis_service.AIOrchestrator.analyze_submission",
        return_value=(_analysis_result(question_id), {"prompt_tokens": 5, "completion_tokens": 5, "latency_ms": 5}, "anthropic", "v1"),
    ):
        analyze_resp = client.post(f"/submissions/{submission['id']}/analyze", headers=headers_t)
    assert analyze_resp.status_code == 201

    client.post(f"/submissions/{submission['id']}/review", headers=headers_t)
    results_resp = client.get(f"/submissions/{submission['id']}/results", headers=headers_s)
    assert results_resp.status_code == 200
    assert results_resp.json()["is_released"] is True