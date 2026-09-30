import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import AssessmentType
from app.models.lesson_plan import LessonPlan
from app.repositories.assessment_repository import AssessmentRepository


class AssessmentService:
    def __init__(self, db: Session):
        self.db = db
        self.assessments = AssessmentRepository(db)

    def create_assessment(self, *, request, teacher):
        lesson_plan = (
            self.db.query(LessonPlan)
            .filter(LessonPlan.id == request.lesson_plan_id, LessonPlan.school_id == teacher.school_id)
            .first()
        )
        if lesson_plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson plan not found.")
        if lesson_plan.teacher_id != teacher.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this lesson plan.")

        questions = [q.model_dump() for q in request.questions]
        assessment = self.assessments.create(
            lesson_plan_id=lesson_plan.id, title=request.title, assessment_type=request.assessment_type, questions=questions
        )
        self.db.commit()
        self.db.refresh(assessment)
        for q in assessment.questions:
            self.db.refresh(q)
        return assessment

    def create_from_lesson_content(self, *, lesson_plan_id: uuid.UUID, teacher):
        """Promotes the AI-generated (JSONB) assessment_questions from Stages 4/6 into real,
        normalized AssessmentQuestion rows — the bridge from generation output to a gradable
        assessment. correct_answer_text is left null for MCQs generated this way, since Stage 6's
        mock/AI output marks correctness via the options list shape, not a separate answer field —
        a teacher can edit questions after this call to add reference answers for short-answer items."""
        lesson_plan = (
            self.db.query(LessonPlan)
            .filter(LessonPlan.id == lesson_plan_id, LessonPlan.school_id == teacher.school_id)
            .first()
        )
        if lesson_plan is None or lesson_plan.teacher_id != teacher.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson plan not found.")
        if lesson_plan.content is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson plan has no generated content yet.")

        questions = [
            {
                "question_text": q["question_text"],
                "question_type": q["question_type"],
                "options": q.get("options"),
                "correct_answer_text": None,
                "max_score": q["max_score"],
                "order_index": i,
            }
            for i, q in enumerate(lesson_plan.content.assessment_questions)
        ]
        assessment = self.assessments.create(
            lesson_plan_id=lesson_plan.id,
            title=f"{lesson_plan.topic} Assessment",
            assessment_type=AssessmentType.FORMATIVE,
            questions=questions,
        )
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_assessment_for_teacher(self, *, assessment_id: uuid.UUID, teacher):
        assessment = self.assessments.get_by_id(assessment_id)
        if assessment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
        lesson_plan = self.db.get(LessonPlan, assessment.lesson_plan_id)
        if lesson_plan.school_id != teacher.school_id or lesson_plan.teacher_id != teacher.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this assessment.")
        return assessment