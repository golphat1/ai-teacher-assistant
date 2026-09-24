"""
Placeholder for the real AI orchestrator that lands in a later stage.

This function's signature and return type (LessonPlanGenerateResponse's content
fields) are exactly what AIOrchestrator.generate_lesson_content(...) will return
once a real provider is wired in — so swapping this out is a one-function change
in the service layer, not a rewrite of routers/schemas/models.
"""
from app.schemas.lesson_plan import (
    AssessmentQuestion,
    DifferentiatedActivity,
    LessonPlanGenerateRequest,
    RubricCriterion,
    TeachingActivity,
)


def generate_mock_lesson_content(request: LessonPlanGenerateRequest) -> dict:
    return {
        "learning_objectives": [
            f"Students will be able to identify key features of {request.topic}.",
            f"Students will be able to analyze a short {request.subject} text related to {request.topic}.",
            f"Students will be able to produce original work demonstrating understanding of {request.topic}.",
        ],
        "teaching_activities": [
            TeachingActivity(
                title="Warm-up discussion",
                description=f"Brief class discussion introducing {request.topic}.",
                duration_minutes=10,
            ).model_dump(),
            TeachingActivity(
                title="Guided practice",
                description=f"Teacher-led walkthrough of a {request.topic} example, "
                             f"scaled for a class of {request.student_count}.",
                duration_minutes=25,
            ).model_dump(),
            TeachingActivity(
                title="Independent activity",
                description="Students work individually or in pairs to apply what was covered.",
                duration_minutes=request.duration_minutes - 35 if request.duration_minutes > 35 else 15,
            ).model_dump(),
        ],
        "differentiated_activities": [
            DifferentiatedActivity(
                target_group="below_grade_level",
                description="Provide a simplified worksheet with guided sentence starters.",
            ).model_dump(),
            DifferentiatedActivity(
                target_group="above_grade_level",
                description="Offer an extension task requiring independent analysis.",
            ).model_dump(),
        ],
        "assessment_questions": [
            AssessmentQuestion(
                question_text=f"Explain one key idea related to {request.topic} in your own words.",
                question_type="short_answer",
                max_score=5,
            ).model_dump(),
            AssessmentQuestion(
                question_text=f"Which of the following best relates to {request.topic}?",
                question_type="mcq",
                options=["Option A", "Option B", "Option C", "Option D"],
                max_score=2,
            ).model_dump(),
        ],
        "marking_rubric": [
            RubricCriterion(
                criterion="Understanding",
                description="Demonstrates clear understanding of the core concept.",
                max_points=5,
            ).model_dump(),
            RubricCriterion(
                criterion="Clarity",
                description="Response is clearly and coherently expressed.",
                max_points=3,
            ).model_dump(),
        ],
        "homework": [
            f"Write a short reflection (150-200 words) applying today's {request.topic} lesson.",
        ],
        "revision_questions": [
            f"What is one thing you learned about {request.topic} today?",
            f"How would you explain {request.topic} to a classmate who missed the lesson?",
        ],
    }