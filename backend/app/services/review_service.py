import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session, selectinload

from app.models.enums import GradeReleasePolicy, SubmissionStatus
from app.models.school import School
from app.models.school_class import SchoolClass
from app.models.score_override_audit import ScoreOverrideAudit
from app.models.submission import StudentSubmission, SubmissionAnswer
from app.models.submission_analysis import SubmissionAnalysis
from app.schemas.review import SubmissionResultsRead


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def _get_submission_or_404(self, submission_id: uuid.UUID, *, school_id: uuid.UUID) -> StudentSubmission:
        submission = (
            self.db.query(StudentSubmission)
            .options(selectinload(StudentSubmission.answers))
            .filter(StudentSubmission.id == submission_id)
            .first()
        )
        if submission is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Submission not found.")
        return submission

    def _assert_teacher_owns(self, submission: StudentSubmission, teacher):
        if submission.assignment.assigned_by != teacher.id:
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You do not own this assignment.")

    def override_score(self, *, submission_id: uuid.UUID, answer_id: uuid.UUID, new_score: float, reason: str | None, teacher):
        submission = self._get_submission_or_404(submission_id, school_id=teacher.school_id)
        self._assert_teacher_owns(submission, teacher)

        answer = next((a for a in submission.answers if a.id == answer_id), None)
        if answer is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Answer not found on this submission.")

        audit = ScoreOverrideAudit(
            submission_answer_id=answer.id,
            previous_score=answer.score,
            new_score=new_score,
            overridden_by=teacher.id,
            reason=reason,
        )
        self.db.add(audit)
        answer.score = new_score
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def mark_reviewed(self, *, submission_id: uuid.UUID, teacher):
        submission = self._get_submission_or_404(submission_id, school_id=teacher.school_id)
        self._assert_teacher_owns(submission, teacher)

        if submission.status != SubmissionStatus.ANALYZED:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot review a submission that has not been analyzed yet.",
            )

        submission.reviewed_by = teacher.id
        submission.reviewed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def _get_school_for_submission(self, submission: StudentSubmission) -> School:
        school_class = self.db.get(SchoolClass, submission.assignment.class_id)
        return self.db.get(School, school_class.school_id)

    def get_results_for_student(self, *, submission_id: uuid.UUID, student) -> SubmissionResultsRead:
        submission = self._get_submission_or_404(submission_id, school_id=student.school_id)
        if submission.student_id != student.id:
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="This is not your submission.")

        school = self._get_school_for_submission(submission)

        if submission.status != SubmissionStatus.ANALYZED:
            return SubmissionResultsRead(is_released=False, message="Your submission has not been graded yet.")

        if school.grade_release_policy == GradeReleasePolicy.REQUIRES_TEACHER_REVIEW and submission.reviewed_at is None:
            return SubmissionResultsRead(
                is_released=False, message="Your results are being reviewed by your teacher and will be released soon."
            )

        analysis = self.db.query(SubmissionAnalysis).filter(SubmissionAnalysis.submission_id == submission.id).first()
        return SubmissionResultsRead(
            is_released=True,
            overall_score=float(analysis.overall_score),
            feedback_text=analysis.feedback_text,
            strengths=analysis.strengths,
            weaknesses=analysis.weaknesses,
            recommendations=analysis.recommendations,
        )