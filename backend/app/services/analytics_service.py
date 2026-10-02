import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.models.assignment import AssessmentAssignment
from app.models.enums import GradeReleasePolicy
from app.models.school import School
from app.models.school_class import SchoolClass
from app.models.submission import StudentSubmission
from app.models.submission_analysis import SubmissionAnalysis
from app.models.user import User
from app.repositories.class_analytics_snapshot_repository import ClassAnalyticsSnapshotRepository

SNAPSHOT_TTL = timedelta(minutes=15)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.snapshots = ClassAnalyticsSnapshotRepository(db)

    def _assert_owns_class(self, class_id: uuid.UUID, teacher) -> SchoolClass:
        school_class = (
            self.db.query(SchoolClass)
            .filter(SchoolClass.id == class_id, SchoolClass.school_id == teacher.school_id)
            .first()
        )
        if school_class is None or school_class.teacher_id != teacher.id:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Class not found.")
        return school_class

    def get_overview(self, *, class_id: uuid.UUID, teacher, force_refresh: bool = False) -> dict:
        self._assert_owns_class(class_id, teacher)

        if not force_refresh:
            cached = self.snapshots.get_latest(class_id)
            if cached and datetime.now(timezone.utc) - cached.generated_at < SNAPSHOT_TTL:
                return self._to_response(cached, is_cached=True)

        analyses = (
            self.db.query(SubmissionAnalysis)
            .join(StudentSubmission, SubmissionAnalysis.submission_id == StudentSubmission.id)
            .join(AssessmentAssignment, StudentSubmission.assignment_id == AssessmentAssignment.id)
            .filter(AssessmentAssignment.class_id == class_id)
            .all()
        )

        scores = [float(a.overall_score) for a in analyses]
        counts: dict[str, int] = {}
        for a in analyses:
            for concept in a.misunderstood_concepts:
                counts[concept] = counts.get(concept, 0) + 1
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]

        snapshot = self.snapshots.create(
            class_id=class_id,
            average_score=(sum(scores) / len(scores)) if scores else None,
            submission_count=len(scores),
            score_distribution=scores,
            common_misconceptions=[{"concept": c, "frequency": f} for c, f in ranked],
            generated_at=datetime.now(timezone.utc),
        )
        self.db.commit()
        self.db.refresh(snapshot)
        return self._to_response(snapshot, is_cached=False)

    @staticmethod
    def _to_response(snapshot, *, is_cached: bool) -> dict:
        return {
            "average_score": float(snapshot.average_score) if snapshot.average_score is not None else None,
            "submission_count": snapshot.submission_count,
            "score_distribution": snapshot.score_distribution,
            "common_misconceptions": snapshot.common_misconceptions,
            "generated_at": snapshot.generated_at,
            "is_cached": is_cached,
        }

    def get_submissions_table(self, *, class_id: uuid.UUID, teacher) -> list[dict]:
        school_class = self._assert_owns_class(class_id, teacher)
        school = self.db.get(School, school_class.school_id)

        from app.models.assessment import Assessment  # local import avoids a circular import at module load

        submissions = (
            self.db.query(StudentSubmission)
            .join(AssessmentAssignment, StudentSubmission.assignment_id == AssessmentAssignment.id)
            .filter(AssessmentAssignment.class_id == class_id)
            .all()
        )

        rows = []
        for submission in submissions:
            student = self.db.get(User, submission.student_id)
            assignment = self.db.get(AssessmentAssignment, submission.assignment_id)
            assessment = self.db.get(Assessment, assignment.assessment_id)
            analysis = (
                self.db.query(SubmissionAnalysis)
                .filter(SubmissionAnalysis.submission_id == submission.id)
                .first()
            )

            if submission.status.value != "analyzed":
                review_status = "not_analyzed"
            elif school.grade_release_policy == GradeReleasePolicy.AUTO_RELEASE:
                review_status = "auto_released"
            elif submission.reviewed_at is not None:
                review_status = "reviewed"
            else:
                review_status = "pending"

            rows.append(
                {
                    "submission_id": submission.id,
                    "student_name": student.full_name,
                    "assignment_title": assessment.title,
                    "status": submission.status.value,
                    "review_status": review_status,
                    "overall_score": float(analysis.overall_score) if analysis else None,
                    "submitted_at": submission.submitted_at,
                    "reviewed_at": submission.reviewed_at,
                }
            )

        rows.sort(key=lambda r: r["submitted_at"], reverse=True)
        return rows