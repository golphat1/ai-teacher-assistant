from app.schemas.lesson_plan import (
    AssessmentQuestion,
    DifferentiatedActivity,
    LessonPlanGenerateRequest,
    RubricCriterion,
    RubricPerformanceLevel,
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
                teacher_actions=f"Poses an opening question about {request.topic} and facilitates discussion.",
                student_actions="Share initial ideas and prior knowledge in a whole-class discussion.",
                duration_minutes=10,
            ).model_dump(),
            TeachingActivity(
                title="Guided practice",
                teacher_actions=f"Models a worked example related to {request.topic} on the board.",
                student_actions="Follow along, ask clarifying questions, take notes.",
                duration_minutes=25,
            ).model_dump(),
            TeachingActivity(
                title="Independent activity",
                teacher_actions="Circulates, checks understanding, and provides individual feedback.",
                student_actions="Work individually or in pairs to apply what was covered.",
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
                performance_levels=[
                    RubricPerformanceLevel(level="Proficient", descriptor="Explains the concept accurately with a relevant example.", points=5),
                    RubricPerformanceLevel(level="Developing", descriptor="Shows partial understanding but lacks a clear example.", points=3),
                    RubricPerformanceLevel(level="Beginning", descriptor="Response is unclear or largely inaccurate.", points=1),
                ],
            ).model_dump(),
            RubricCriterion(
                criterion="Clarity",
                description="Response is clearly and coherently expressed.",
                max_points=3,
                performance_levels=[
                    RubricPerformanceLevel(level="Proficient", descriptor="Well-organized and easy to follow.", points=3),
                    RubricPerformanceLevel(level="Developing", descriptor="Understandable but somewhat disorganized.", points=1),
                ],
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