PROMPT_VERSION = "lesson_generation_v1"

SYSTEM_PROMPT = """You are an experienced curriculum designer helping a teacher plan a lesson.

- Learning objectives must be specific and measurable. Use verbs like "identify", "analyze",
  "compare", "produce" — avoid vague verbs like "understand" or "learn about".
- Teaching activities must clearly state what the TEACHER does vs what STUDENTS do, and
  activity durations should sum to roughly the requested lesson duration.
- Differentiated activities must address at least a below-grade-level and an above-grade-level group.
- Assessment questions must be answerable using only what was covered in this lesson — do not
  introduce concepts outside the requested topic.
- Only reference curriculum standards if a curriculum was explicitly provided. Never invent
  standard codes.
- Return ONLY the structured result via the provided schema — no prose outside it."""


def build_user_prompt(request) -> str:
    parts = [
        f"Grade: {request.grade}",
        f"Subject: {request.subject}",
        f"Topic: {request.topic}",
        f"Class size: {request.student_count} students",
        f"Lesson duration: {request.duration_minutes} minutes",
        f"Student ability level: {request.ability_level}",
    ]
    if request.curriculum:
        parts.append(f"Curriculum: {request.curriculum}")
    if request.learning_context:
        parts.append(f"Learning context: {request.learning_context}")
    if request.additional_instructions:
        parts.append(f"Additional teacher instructions: {request.additional_instructions}")
    return "\n".join(parts)