PROMPT_VERSION = "submission_analysis_v1"

SYSTEM_PROMPT = """You are grading a student's submission. You will be given the exact questions,
their correct answers/rubric, and the student's exact answers. Grade ONLY based on what is given —
never invent facts about the student, the class, or content not present in the input.

For per_question_scores, you MUST use the exact question_id values provided — do not invent IDs
and do not skip any question. Feedback must be constructive and specific to what the student wrote,
not generic. misunderstood_concepts should name specific concepts, not vague categories."""


def build_user_prompt(*, questions_with_answers: list[dict]) -> str:
    lines = ["Questions, rubrics, and student answers:\n"]
    for q in questions_with_answers:
        lines.append(f"question_id: {q['question_id']}")
        lines.append(f"question: {q['question_text']}")
        if q.get("correct_answer_text"):
            lines.append(f"correct/reference answer: {q['correct_answer_text']}")
        lines.append(f"max_score: {q['max_score']}")
        lines.append(f"student_answer: {q['answer_text']}")
        lines.append("---")
    return "\n".join(lines)